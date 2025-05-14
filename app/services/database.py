from supabase import create_client, Client
from ..config import settings
from typing import Optional, List, Dict, Any
import datetime
import uuid

supabase_storage: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

class DatabaseService:
    def __init__(self):
        self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        response = self.supabase.table("users").select("*").eq("email", email).execute()
        return response.data[0] if response.data else None

    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        response = self.supabase.table("users").insert(user_data).execute()
        return response.data[0]

    async def get_projects(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all projects for a user, including client name"""
        response = self.supabase.table("projects").select("*, clients(name)").eq("user_id", user_id).execute()
        projects = response.data
        for project in projects:
            project["client_name"] = project["clients"]["name"] if project.get("clients") else ""
            if "clients" in project:
                del project["clients"]
        return projects

    async def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific project by ID"""
        response = self.supabase.table("projects").select("*").eq("id", project_id).execute()
        return response.data[0] if response.data else None

    async def create_project(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new project"""
        # Convert UUID fields to strings if needed
        if 'client_id' in data and hasattr(data['client_id'], 'hex'):
            data['client_id'] = str(data['client_id'])
        # Convert datetime fields to ISO strings if needed
        for key in ['start_date', 'end_date', 'created_at', 'updated_at']:
            if key in data and isinstance(data[key], datetime.datetime):
                data[key] = data[key].isoformat()
        response = self.supabase.table("projects").insert(data).execute()
        return response.data[0]

    async def update_project(self, project_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a project"""
        data = self.to_serializable(data)
        response = self.supabase.table("projects").update(data).eq("id", project_id).execute()
        return response.data[0]

    async def delete_project(self, project_id: str) -> bool:
        """Delete a project"""
        response = self.supabase.table("projects").delete().eq("id", project_id).execute()
        return bool(response.data)

    async def get_project_tasks(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all tasks for a project"""
        response = self.supabase.table("tasks").select("*").eq("project_id", project_id).execute()
        return response.data

    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific task by ID"""
        response = self.supabase.table("tasks").select("*").eq("id", task_id).execute()
        return response.data[0] if response.data else None

    async def create_task(self, project_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new task"""
        task_data = {**data, "project_id": project_id}
        # Remove category_id if present
        task_data.pop("category_id", None)
        # Convert datetime fields to ISO strings if needed
        for key in ['due_date', 'created_at', 'updated_at']:
            if key in task_data and isinstance(task_data[key], datetime.datetime):
                task_data[key] = task_data[key].isoformat()
        response = self.supabase.table("tasks").insert(task_data).execute()
        return response.data[0]

    async def update_task(self, task_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a task"""
        data = self.to_serializable(data)
        response = self.supabase.table("tasks").update(data).eq("id", task_id).execute()
        return response.data[0]

    async def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        response = self.supabase.table("tasks").delete().eq("id", task_id).execute()
        return bool(response.data)

    async def get_task_time_entries(self, task_id: str) -> List[Dict[str, Any]]:
        """Get all time entries for a task, including their files"""
        response = self.supabase.table("time_entries").select(
            "*, tasks(*), time_entry_files(*)"
        ).eq("task_id", task_id).execute()
        return response.data

    async def create_time_entry(self, task_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new time entry"""
        time_entry_data = {**data, "task_id": task_id}
        time_entry_data = self.to_serializable(time_entry_data)
        response = self.supabase.table("time_entries").insert(time_entry_data).execute()
        return response.data[0]

    async def update_time_entry(self, time_entry_id: str, time_entry_data: Dict[str, Any]) -> Dict[str, Any]:
        time_entry_data = self.to_serializable(time_entry_data)
        response = self.supabase.table("time_entries").update(time_entry_data).eq("id", time_entry_id).execute()
        return response.data[0]

    async def delete_time_entry(self, time_entry_id: str) -> None:
        self.supabase.table("time_entries").delete().eq("id", time_entry_id).execute()

    async def get_time_entry(self, time_entry_id: str) -> Optional[Dict[str, Any]]:
        response = self.supabase.table("time_entries").select("*").eq("id", time_entry_id).execute()
        return response.data[0] if response.data else None

    async def get_category(self, category_id: str) -> Optional[Dict[str, Any]]:
        response = self.supabase.table("categories").select("*").eq("id", category_id).execute()
        return response.data[0] if response.data else None

    async def get_categories(self, user_id: str) -> List[Dict[str, Any]]:
        response = self.supabase.table("categories").select("*").eq("user_id", user_id).execute()
        return response.data

    async def create_category(self, category_data: Dict[str, Any]) -> Dict[str, Any]:
        response = self.supabase.table("categories").insert(category_data).execute()
        return response.data[0]

    async def update_category(self, category_id: str, category_data: Dict[str, Any]) -> Dict[str, Any]:
        response = self.supabase.table("categories").update(category_data).eq("id", category_id).execute()
        return response.data[0]

    async def delete_category(self, category_id: str) -> None:
        self.supabase.table("categories").delete().eq("id", category_id).execute()

    async def get_client(self, client_id: str) -> Optional[Dict[str, Any]]:
        response = self.supabase.table("clients").select("*").eq("id", client_id).execute()
        return response.data[0] if response.data else None

    async def get_clients(self, user_id: str) -> List[Dict[str, Any]]:
        response = self.supabase.table("clients").select("*").eq("user_id", user_id).execute()
        return response.data

    async def create_client(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        response = self.supabase.table("clients").insert(client_data).execute()
        return response.data[0]

    async def update_client(self, client_id: str, client_data: Dict[str, Any]) -> Dict[str, Any]:
        response = self.supabase.table("clients").update(client_data).eq("id", client_id).execute()
        return response.data[0]

    async def delete_client(self, client_id: str) -> None:
        self.supabase.table("clients").delete().eq("id", client_id).execute()

    async def get_client_projects(self, client_id: str) -> List[Dict[str, Any]]:
        response = self.supabase.table("projects").select("*").eq("client_id", client_id).execute()
        return response.data

    async def get_team_member(self, team_member_id: str) -> Optional[Dict[str, Any]]:
        response = self.supabase.table("team_members").select("*").eq("id", team_member_id).execute()
        return response.data[0] if response.data else None

    async def get_project_team_members(self, project_id: str) -> List[Dict[str, Any]]:
        response = self.supabase.table("team_members").select("*").eq("project_id", project_id).execute()
        return response.data

    async def get_user_team_memberships(self, user_id: str) -> List[Dict[str, Any]]:
        response = self.supabase.table("team_members").select("*").eq("user_id", user_id).execute()
        return response.data

    async def create_team_member(self, team_member_data: Dict[str, Any]) -> Dict[str, Any]:
        response = self.supabase.table("team_members").insert(team_member_data).execute()
        return response.data[0]

    async def update_team_member(self, team_member_id: str, team_member_data: Dict[str, Any]) -> Dict[str, Any]:
        response = self.supabase.table("team_members").update(team_member_data).eq("id", team_member_id).execute()
        return response.data[0]

    async def delete_team_member(self, team_member_id: str) -> None:
        self.supabase.table("team_members").delete().eq("id", team_member_id).execute()

    async def get_team_member_with_user(self, team_member_id: str) -> Optional[Dict[str, Any]]:
        response = self.supabase.table("team_members").select("*, users(*)").eq("id", team_member_id).execute()
        return response.data[0] if response.data else None

    async def get_team_member_with_project(self, team_member_id: str) -> Optional[Dict[str, Any]]:
        response = self.supabase.table("team_members").select("*, projects(*)").eq("id", team_member_id).execute()
        return response.data[0] if response.data else None

    async def get_team_member_with_details(self, team_member_id: str) -> Optional[Dict[str, Any]]:
        response = self.supabase.table("team_members").select("*, users(*), projects(*)").eq("id", team_member_id).execute()
        return response.data[0] if response.data else None

    # Report methods
    async def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        response = self.supabase.table("reports").select("*").eq("id", report_id).execute()
        return response.data[0] if response.data else None

    async def get_reports(self, user_id: str) -> List[Dict[str, Any]]:
        response = self.supabase.table("reports").select("*").eq("user_id", user_id).execute()
        return response.data

    async def create_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        response = self.supabase.table("reports").insert(report_data).execute()
        return response.data[0]

    async def update_report(self, report_id: str, report_data: Dict[str, Any]) -> Dict[str, Any]:
        response = self.supabase.table("reports").update(report_data).eq("id", report_id).execute()
        return response.data[0]

    async def delete_report(self, report_id: str) -> None:
        self.supabase.table("reports").delete().eq("id", report_id).execute()

    async def get_time_entries_for_report(
        self,
        start_date: str,
        end_date: str,
        project_ids: Optional[List[str]] = None,
        team_member_ids: Optional[List[str]] = None,
        client_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        query = self.supabase.table("time_entries").select(
            "*, tasks(*, projects(*, clients(*))), users(*), time_entry_files(*)"
        ).gte("date", start_date).lte("date", end_date)

        if project_ids:
            query = query.in_("task.project_id", project_ids)
        if team_member_ids:
            query = query.in_("user_id", team_member_ids)
        if client_ids:
            query = query.in_("task.project.client_id", client_ids)

        response = query.execute()
        return response.data

    async def get_projects_for_report(
        self,
        project_ids: Optional[List[str]] = None,
        client_ids: Optional[List[str]] = None,
        include_inactive: bool = False
    ) -> List[Dict[str, Any]]:
        query = self.supabase.table("projects").select("*, clients(*), team_members(*, users(*))")
        
        if project_ids:
            query = query.in_("id", project_ids)
        if client_ids:
            query = query.in_("client_id", client_ids)
        if not include_inactive:
            query = query.eq("is_active", True)

        response = query.execute()
        return response.data

    async def get_team_members_for_report(
        self,
        project_ids: Optional[List[str]] = None,
        team_member_ids: Optional[List[str]] = None,
        include_inactive: bool = False
    ) -> List[Dict[str, Any]]:
        query = self.supabase.table("team_members").select("*, users(*), projects(*)")
        
        if project_ids:
            query = query.in_("project_id", project_ids)
        if team_member_ids:
            query = query.in_("user_id", team_member_ids)
        if not include_inactive:
            query = query.eq("is_active", True)

        response = query.execute()
        return response.data

    async def get_clients_for_report(
        self,
        client_ids: Optional[List[str]] = None,
        include_inactive: bool = False
    ) -> List[Dict[str, Any]]:
        query = self.supabase.table("clients").select("*, projects(*)")
        
        if client_ids:
            query = query.in_("id", client_ids)
        if not include_inactive:
            query = query.eq("is_active", True)

        response = query.execute()
        return response.data

    # Notification methods
    async def get_notification(self, notification_id: str) -> Optional[Dict[str, Any]]:
        response = self.supabase.table("notifications").select("*").eq("id", notification_id).execute()
        return response.data[0] if response.data else None

    async def get_user_notifications(
        self,
        user_id: str,
        is_read: Optional[bool] = None,
        is_archived: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        query = self.supabase.table("notifications").select("*").eq("user_id", user_id)
        
        if is_read is not None:
            query = query.eq("is_read", is_read)
        if is_archived is not None:
            query = query.eq("is_archived", is_archived)
        
        query = query.order("created_at", desc=True).range(offset, offset + limit - 1)
        response = query.execute()
        return response.data

    async def create_notification(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        response = self.supabase.table("notifications").insert(notification_data).execute()
        return response.data[0]

    async def update_notification(self, notification_id: str, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        response = self.supabase.table("notifications").update(notification_data).eq("id", notification_id).execute()
        return response.data[0]

    async def delete_notification(self, notification_id: str) -> None:
        self.supabase.table("notifications").delete().eq("id", notification_id).execute()

    async def mark_notifications_as_read(self, user_id: str, notification_ids: Optional[List[str]] = None) -> None:
        query = self.supabase.table("notifications").update({
            "is_read": True,
            "read_at": datetime.datetime.now().isoformat()
        }).eq("user_id", user_id)
        
        if notification_ids:
            query = query.in_("id", notification_ids)
        
        query.execute()

    async def archive_notifications(self, user_id: str, notification_ids: Optional[List[str]] = None) -> None:
        query = self.supabase.table("notifications").update({
            "is_archived": True
        }).eq("user_id", user_id)
        
        if notification_ids:
            query = query.in_("id", notification_ids)
        
        query.execute()

    async def get_notification_preference(self, user_id: str) -> Optional[Dict[str, Any]]:
        response = self.supabase.table("notification_preferences").select("*").eq("user_id", user_id).execute()
        return response.data[0] if response.data else None

    async def create_notification_preference(self, preference_data: Dict[str, Any]) -> Dict[str, Any]:
        response = self.supabase.table("notification_preferences").insert(preference_data).execute()
        return response.data[0]

    async def update_notification_preference(self, user_id: str, preference_data: Dict[str, Any]) -> Dict[str, Any]:
        response = self.supabase.table("notification_preferences").update(preference_data).eq("user_id", user_id).execute()
        return response.data[0]

    async def create_client_file(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        response = self.supabase.table("client_files").insert(file_data).execute()
        return response.data[0]

    async def get_client_files(self, client_id: str) -> List[Dict[str, Any]]:
        response = self.supabase.table("client_files").select("*").eq("client_id", client_id).order("uploaded_at", desc=True).execute()
        return response.data

    async def delete_client_file(self, file_id: str) -> None:
        self.supabase.table("client_files").delete().eq("id", file_id).execute()

    def to_serializable(self, data):
        """Convert data to JSON serializable format"""
        if isinstance(data, dict):
            return {k: self.to_serializable(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.to_serializable(item) for item in data]
        elif isinstance(data, datetime.datetime):
            return data.isoformat()
        elif isinstance(data, uuid.UUID):
            return str(data)
        return data

    async def get_active_tasks_for_projects(self, project_ids: List[str]) -> List[Dict[str, Any]]:
        """Get all active tasks for a list of project IDs"""
        print("DEBUG: project_ids for active tasks:", project_ids)
        # Filter out any empty or invalid IDs
        project_ids = [pid for pid in project_ids if pid and len(pid) >= 32]
        print("DEBUG: project_ids for active tasks:", project_ids)
        if not project_ids:
            return []
        response = self.supabase.table("tasks").select("*") \
            .in_("project_id", project_ids) \
            .eq("status", "in_progress") \
            .execute()
        return response.data

# Create a singleton instance
db = DatabaseService() 