"""
Feature 2: Business bot for project management.
Functionality: Helps track project progress and deadlines.
Use Cases: Managers overseeing multiple projects.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import uuid
from core.bot_base import AutonomyLevel, BotBase, ScalingLevel


class ProjectManagementBot(BotBase):
    """Tracks project progress, tasks, and deadlines."""

    def __init__(self) -> None:
        super().__init__("ProjectManagementBot", AutonomyLevel.SEMI_AUTONOMOUS, ScalingLevel.MODERATE)
        self._projects: dict = {}

    def create_project(self, name: str, deadline: str, owner: str) -> dict:
        """Create a new project entry."""
        pid = str(uuid.uuid4())
        self._projects[pid] = {
            "project_id": pid, "name": name, "deadline": deadline,
            "owner": owner, "tasks": [], "progress": 0,
        }
        return {"status": "ok", "project_id": pid, "name": name}

    def add_task(self, project_id: str, task_name: str, assignee: str) -> dict:
        """Add a task to a project."""
        project = self._projects.get(project_id)
        if not project:
            return {"status": "error", "message": "Project not found"}
        task = {"task_id": str(uuid.uuid4()), "name": task_name, "assignee": assignee, "done": False}
        project["tasks"].append(task)
        return {"status": "ok", "task_id": task["task_id"]}

    def complete_task(self, project_id: str, task_id: str) -> dict:
        """Mark a task as complete and recalculate project progress."""
        project = self._projects.get(project_id)
        if not project:
            return {"status": "error", "message": "Project not found"}
        for task in project["tasks"]:
            if task["task_id"] == task_id:
                task["done"] = True
        done = sum(1 for t in project["tasks"] if t["done"])
        total = len(project["tasks"])
        project["progress"] = round(done / total * 100) if total else 0
        return {"status": "ok", "progress": project["progress"]}

    def _run_task(self, task: dict) -> dict:
        if task.get("type") == "create_project":
            return self.create_project(task.get("name", ""), task.get("deadline", ""), task.get("owner", ""))
        return super()._run_task(task)


if __name__ == "__main__":
    bot = ProjectManagementBot()
    bot.start()
    proj = bot.create_project("Platform Launch", "2026-06-01", "alice")
    bot.add_task(proj["project_id"], "Design mockups", "bob")
    print(bot._projects)
    bot.stop()