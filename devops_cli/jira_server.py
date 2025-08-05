"""
JiraServer integration for Digitalworks2020 DevOps CLI.
Lists current sprint name for a given project using OOP and python-jira.
Follows PEP8, Codacy, and Copilot workspace instructions for maintainability and reliability.
"""
from jira import JIRA
from typing import Optional, Any
import requests

class JiraServerClient:
    """
    JiraServerClient provides methods to interact with Jira Server boards and sprints.
    """
    def __init__(self, url: str, api_token: str) -> None:
        """Initialize JiraServerClient with credentials."""
        self.url = url
        self.api_token = api_token
        self.jira = JIRA(server=url, token_auth = api_token, validate=True)

    def get_sprint_story_points_stats(self, board_name: str, num_sprints: int = 3) -> Optional[list[dict]]:
        """
        Get committed SP, achieved SP, and average SP for the last num_sprints closed sprints on the board using Jira sprint report.
        Args:
            board_name (str): The name of the Jira board.
            num_sprints (int): Number of last closed sprints to analyze.
        Returns:
            List of dicts with sprint name, committed SP, achieved SP, and average SP.
        """
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Accept": "application/json"
        }
        board_id = self.get_board_id(board_name)
        if board_id is None:
            print(f"Board '{board_name}' not found.")
            return None
        stats = []
        try:
            report_json = requests.get(
                f'{self.url}/rest/greenhopper/1.0/rapid/charts/velocity?rapidViewId={board_id}',
                headers = headers
                ).json()
        except Exception as exc:
            print(f"Error fetching sprint report for {sprint_name}: {exc}")
            return None
        # Directly relay values from the report
        # Get last 3 sprints
        sprints = report_json.get("sprints", [])[-3:]
        for sprint in sprints:
            name, sprint_id = (sprint["name"], sprint["id"])
            sprint_data = next(
                (d for d in report_json["velocityStatEntries"].values() if d["sprintId"] == sprint_id),
                None
            )
            if not sprint_data:
                continue
            stats.append({
                "sprint": name,
                "committed_sp" : sprint_data["estimated"]["value"],
                "achieved_sp"  : sprint_data["completed"]["value"]
            })
        avg_velocity = sum(s["achieved_sp"] for s in stats) / len(stats)
        return stats, avg_velocity


    def get_my_issues_in_current_sprint(self, board_name: str, max_results: int = 50) -> Optional[list[Any]]:
        """
        Get issues assigned to the current user in the current active sprint for the given board.
        Handles pagination.
        Args:
            board_name (str): The name of the Jira board.
            max_results (int): Maximum number of issues per page.
        Returns:
            List of issues assigned to the current user in the current sprint, or None if error.
        """
        board_id = self.get_board_id(board_name)
        if board_id is None:
            print(f"Board '{board_name}' not found.")
            return None
        sprint = self.get_active_sprint(board_id)
        if sprint is None:
            print(f"No active sprint found for board '{board_name}'.")
            return None
        sprint_id = getattr(sprint, 'id', None)
        if sprint_id is None:
            print("Sprint ID not found.")
            return None
        jql = f"assignee = currentUser() AND sprint = {sprint_id}"
        all_issues = []
        start_at = 0
        while True:
            try:
                issues = self.jira.search_issues(jql, startAt=start_at, maxResults=max_results)
            except Exception as exc:
                print(f"Error fetching issues for current user in sprint: {exc}")
                return None
            all_issues.extend(issues)
            if len(issues) < max_results:
                break
            start_at += max_results
        return all_issues

    def get_active_sprint(self, board_id: int) -> Optional[Any]:
        """
        Get the current active sprint for a given board ID.
        Args:
            board_id (int): The ID of the Jira board.
        Returns:
            The active sprint object if found, else None.
        """
        start_at = 0
        max_results = 50
        while True:
            try:
                sprints = self.jira.sprints(board_id, startAt=start_at, maxResults=max_results)
            except Exception as exc:
                print(f"Error fetching sprints: {exc}")
                return None
            for sprint in sprints:
                if getattr(sprint, 'state', None) == 'active':
                    return sprint
            if len(sprints) < max_results:
                break
            start_at += max_results
        return None

    def get_board_id(self, board_name: str) -> Optional[int]:
        """
        Get the board ID for a given board name.
        Args:
            board_name (str): The name of the Jira board.
        Returns:
            The board ID if found, else None.
        """
        start_at = 0
        max_results = 50
        board_name_lower = board_name.lower()
        while True:
            try:
                boards = self.jira.boards(startAt=start_at, maxResults=max_results)
            except Exception as exc:
                print(f"Error fetching boards: {exc}")
                return None
            for board in boards:
                if getattr(board, 'name', '').lower() == board_name_lower:
                    return getattr(board, 'id', None)
            if len(boards) < max_results:
                break
            start_at += max_results
        return None

    def get_current_sprint_name(self, project_key: str, board_name: str) -> Optional[str]:
        """
        Get the current active sprint name for a given project key and board name.
        Args:
            project_key (str): The Jira project key.
            board_name (str): The name of the Jira board.
        Returns:
            The name of the current active sprint if found, else None.
        """
        board_id = self.get_board_id(board_name)
        if board_id is None:
            print(f"Board '{board_name}' not found.")
            return None
        sprint = self.get_active_sprint(board_id)
        if sprint is None:
            print(f"No active sprint found for board '{board_name}'.")
            return None
        return getattr(sprint, 'name', None)
