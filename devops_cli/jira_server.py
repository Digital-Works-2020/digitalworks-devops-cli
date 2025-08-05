"""
JiraServer integration for Digitalworks2020 DevOps CLI.
Lists current sprint name for a given project using OOP and python-jira.
Follows PEP8, Codacy, and Copilot workspace instructions for maintainability and reliability.
"""
from jira import JIRA
from typing import Optional, Any

class JiraServerClient:
    """
    JiraServerClient provides methods to interact with Jira Server boards and sprints.
    """
    def __init__(self, url: str, api_token: str) -> None:
        """Initialize JiraServerClient with credentials."""
        self.jira = JIRA(server=url, token_auth = api_token, validate=True)

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
