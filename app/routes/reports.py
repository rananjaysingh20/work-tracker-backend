from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Any, Dict, Optional
from datetime import datetime, date, timedelta
from ..schemas.report import (
    Report, ReportCreate, ReportUpdate,
    TimeTrackingReport, ProjectStatsReport,
    TeamProductivityReport, ClientBillingReport,
    TimeRange
)
from ..schemas.user import User
from ..services.database import db
from .auth import get_current_user

router = APIRouter()

def get_date_range(time_range: TimeRange, start_date: Optional[date] = None, end_date: Optional[date] = None) -> tuple[date, date]:
    today = date.today()
    
    if time_range == TimeRange.TODAY:
        return today, today
    elif time_range == TimeRange.YESTERDAY:
        yesterday = today - timedelta(days=1)
        return yesterday, yesterday
    elif time_range == TimeRange.THIS_WEEK:
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        return start, end
    elif time_range == TimeRange.LAST_WEEK:
        start = today - timedelta(days=today.weekday() + 7)
        end = start + timedelta(days=6)
        return start, end
    elif time_range == TimeRange.THIS_MONTH:
        start = date(today.year, today.month, 1)
        if today.month == 12:
            end = date(today.year + 1, 1, 1) - timedelta(days=1)
        else:
            end = date(today.year, today.month + 1, 1) - timedelta(days=1)
        return start, end
    elif time_range == TimeRange.LAST_MONTH:
        if today.month == 1:
            start = date(today.year - 1, 12, 1)
            end = date(today.year, 1, 1) - timedelta(days=1)
        else:
            start = date(today.year, today.month - 1, 1)
            end = date(today.year, today.month, 1) - timedelta(days=1)
        return start, end
    elif time_range == TimeRange.CUSTOM:
        if not start_date or not end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start date and end date are required for custom time range"
            )
        return start_date, end_date
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid time range"
        )

# @router.get("/", response_model=List[Report])
# async def get_reports(
#     current_user: User = Depends(get_current_user)
# ) -> Any:
#     return await db.get_reports(str(current_user.id))

# @router.post("/", response_model=Report)
# async def create_report(
#     report: ReportCreate,
#     current_user: User = Depends(get_current_user)
# ) -> Any:
#     report_data = report.dict()
#     report_data["user_id"] = str(current_user.id)
#     return await db.create_report(report_data)

# @router.get("/{report_id}", response_model=Report)
# async def get_report(
#     report_id: str,
#     current_user: User = Depends(get_current_user)
# ) -> Any:
#     report = await db.get_report(report_id)
#     if not report:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Report not found"
#         )
#     if report["user_id"] != str(current_user.id):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not enough permissions"
#         )
#     return report

# @router.put("/{report_id}", response_model=Report)
# async def update_report(
#     report_id: str,
#     report: ReportUpdate,
#     current_user: User = Depends(get_current_user)
# ) -> Any:
#     existing_report = await db.get_report(report_id)
#     if not existing_report:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Report not found"
#         )
#     if existing_report["user_id"] != str(current_user.id):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not enough permissions"
#         )
#     report_data = report.dict(exclude_unset=True)
#     return await db.update_report(report_id, report_data)

# @router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_report(
#     report_id: str,
#     current_user: User = Depends(get_current_user)
# ) -> None:
#     report = await db.get_report(report_id)
#     if not report:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Report not found"
#         )
#     if report["user_id"] != str(current_user.id):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not enough permissions"
#         )
#     await db.delete_report(report_id)

@router.post("/generate/time-tracking", response_model=TimeTrackingReport)
async def generate_time_tracking_report(
    report: ReportCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    start_date, end_date = get_date_range(report.time_range, report.start_date, report.end_date)
    
    time_entries = await db.get_time_entries_for_report(
        start_date.isoformat(),
        end_date.isoformat(),
        [str(pid) for pid in report.project_ids] if report.project_ids else None,
        [str(tid) for tid in report.team_member_ids] if report.team_member_ids else None,
        [str(cid) for cid in report.client_ids] if report.client_ids else None
    )
    
    total_hours = sum(entry["duration"] for entry in time_entries)
    billable_hours = sum(entry["duration"] for entry in time_entries if entry["is_billable"])
    non_billable_hours = total_hours - billable_hours
    
    # Group entries by the specified field
    summary = {}
    if report.group_by:
        grouped_entries = {}
        for entry in time_entries:
            key = str(entry.get(report.group_by, {}).get("id", "unknown"))
            if key not in grouped_entries:
                grouped_entries[key] = {
                    "total_hours": 0,
                    "billable_hours": 0,
                    "non_billable_hours": 0,
                    "entries": []
                }
            grouped_entries[key]["total_hours"] += entry["duration"]
            if entry["is_billable"]:
                grouped_entries[key]["billable_hours"] += entry["duration"]
            else:
                grouped_entries[key]["non_billable_hours"] += entry["duration"]
            grouped_entries[key]["entries"].append(entry)
        summary = grouped_entries
    
    return TimeTrackingReport(
        total_hours=total_hours,
        billable_hours=billable_hours,
        non_billable_hours=non_billable_hours,
        entries=time_entries,
        summary=summary
    )

@router.post("/generate/project-stats", response_model=ProjectStatsReport)
async def generate_project_stats_report(
    report: ReportCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    projects = await db.get_projects_for_report(
        [str(pid) for pid in report.project_ids] if report.project_ids else None,
        [str(cid) for cid in report.client_ids] if report.client_ids else None,
        report.include_inactive
    )
    
    total_projects = len(projects)
    active_projects = sum(1 for p in projects if p["is_active"])
    completed_projects = sum(1 for p in projects if p["status"] == "completed")
    
    total_hours = 0
    billable_amount = 0
    
    for project in projects:
        time_entries = await db.get_time_entries_for_report(
            report.start_date.isoformat() if report.start_date else "1970-01-01",
            report.end_date.isoformat() if report.end_date else datetime.now().isoformat(),
            [project["id"]]
        )
        project["total_hours"] = sum(entry["duration"] for entry in time_entries)
        project["billable_hours"] = sum(entry["duration"] for entry in time_entries if entry["is_billable"])
        project["billable_amount"] = project["billable_hours"] * project.get("hourly_rate", 0)
        
        total_hours += project["total_hours"]
        billable_amount += project["billable_amount"]
    
    return ProjectStatsReport(
        total_projects=total_projects,
        active_projects=active_projects,
        completed_projects=completed_projects,
        total_hours=total_hours,
        billable_amount=billable_amount,
        projects=projects
    )

@router.post("/generate/team-productivity", response_model=TeamProductivityReport)
async def generate_team_productivity_report(
    report: ReportCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    team_members = await db.get_team_members_for_report(
        [str(pid) for pid in report.project_ids] if report.project_ids else None,
        [str(tid) for tid in report.team_member_ids] if report.team_member_ids else None,
        report.include_inactive
    )
    
    total_members = len(team_members)
    total_hours = 0
    
    for member in team_members:
        time_entries = await db.get_time_entries_for_report(
            report.start_date.isoformat() if report.start_date else "1970-01-01",
            report.end_date.isoformat() if report.end_date else datetime.now().isoformat(),
            [str(pid) for pid in report.project_ids] if report.project_ids else None,
            [member["user_id"]]
        )
        member["total_hours"] = sum(entry["duration"] for entry in time_entries)
        member["billable_hours"] = sum(entry["duration"] for entry in time_entries if entry["is_billable"])
        total_hours += member["total_hours"]
    
    return TeamProductivityReport(
        total_members=total_members,
        total_hours=total_hours,
        average_hours_per_member=total_hours / total_members if total_members > 0 else 0,
        members=team_members
    )

@router.post("/generate/client-billing", response_model=ClientBillingReport)
async def generate_client_billing_report(
    report: ReportCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    clients = await db.get_clients_for_report(
        [str(cid) for cid in report.client_ids] if report.client_ids else None,
        report.include_inactive
    )
    
    total_clients = len(clients)
    total_billable_amount = 0
    total_hours = 0
    
    for client in clients:
        time_entries = await db.get_time_entries_for_report(
            report.start_date.isoformat() if report.start_date else "1970-01-01",
            report.end_date.isoformat() if report.end_date else datetime.now().isoformat(),
            [p["id"] for p in client["projects"]],
            [str(tid) for tid in report.team_member_ids] if report.team_member_ids else None
        )
        client["total_hours"] = sum(entry["duration"] for entry in time_entries)
        client["billable_hours"] = sum(entry["duration"] for entry in time_entries if entry["is_billable"])
        client["billable_amount"] = client["billable_hours"] * client.get("hourly_rate", 0)
        
        total_hours += client["total_hours"]
        total_billable_amount += client["billable_amount"]
    
    return ClientBillingReport(
        total_clients=total_clients,
        total_billable_amount=total_billable_amount,
        total_hours=total_hours,
        clients=clients
    )

@router.get("/clients-full-report", response_model=List[dict])
async def get_clients_full_report(current_user: User = Depends(get_current_user)) -> Any:
    clients = await db.get_clients(str(current_user.id))
    result = []
    for client in clients:
        client_id = client['id']
        projects = await db.get_client_projects(client_id)
        project_list = []
        for project in projects:
            project_id = project['id']
            tasks = await db.get_project_tasks(project_id)
            task_list = []
            for task in tasks:
                task_id = task['id']
                time_entries = await db.get_task_time_entries(task_id)
                task_list.append({
                    **task,
                    'time_entries': time_entries
                })
            project_list.append({
                **project,
                'tasks': task_list
            })
        # Fetch client files and add to client object
        client_files = await db.get_client_files(client_id)
        result.append({
            **client,
            'projects': project_list,
            'client_files': client_files
        })
    return result 