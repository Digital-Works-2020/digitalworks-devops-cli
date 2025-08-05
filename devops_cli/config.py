
"""
Config management for Digitalworks2020 DevOps CLI.
Supports modular, secure, and scalable account setup for multiple tools.
Follows PEP8 and Codacy standards.
"""


import os
import json
import getpass
import tempfile
import shutil
from typing import Dict, Any, Callable, Optional, Tuple


TOOL_CONFIGS: Dict[str, Dict[str, Any]] = {
    "jira_cloud": {
        "fields": [
            {"name": "url", "prompt": "Cloud URL", "secure": False},
            {"name": "username", "prompt": "Cloud username", "secure": False},
            {"name": "api_token", "prompt": "Cloud API token", "secure": True}
        ]
    },
    "jira_server": {
        "fields": [
            {"name": "url", "prompt": "Server URL", "secure": False},
            {"name": "api_token", "prompt": "Server API Token", "secure": True}
        ],
        "operations": [
            {"key": "current_sprint_name", "label": "Display current sprint name"},
            {"key": "my_issues_in_sprint", "label": "List my issues in current sprint"},
            {"key": "sprint_sp_stats", "label": "Get SP for Last 3 Sprint Stats"}
        ]
    },
    # Future: Add 'aws', etc.
}

CONFIG_PATH: str = os.path.expanduser("~/.digitalworks_devops_cli_config.json")
SUPPORTED_TOOLS: list[str] = ["jira_cloud", "jira_server"]  # Extendable for future tools

def atomic_write_config(config: Dict[str, Any]) -> None:
    """
    Atomically write config to disk.
    Args:
        config (dict): The configuration dictionary to write.
    """
    temp_fd, temp_path = tempfile.mkstemp()
    with os.fdopen(temp_fd, 'w') as tmp_file:
        json.dump(config, tmp_file, indent=2)
    shutil.move(temp_path, CONFIG_PATH)

def prompt_for_account(tool: str, account_name: str, prompt_input: Callable = input) -> Dict[str, str]:
    """
    Prompt user for account credentials for the given tool.
    Args:
        tool (str): Tool name.
        account_name (str): Account name.
        prompt_input (Callable): Input function (default: input).
    Returns:
        dict: Credentials dictionary.
    """
    fields = TOOL_CONFIGS[tool]["fields"]
    creds: Dict[str, str] = {}
    for field in fields:
        if field["secure"]:
            value = getpass.getpass(f"Enter {tool.replace('_', ' ').title()} {field['prompt']} for '{account_name}': ")
        else:
            value = prompt_input(f"Enter {tool.replace('_', ' ').title()} {field['prompt']} for '{account_name}': ").strip()
        creds[field["name"]] = value
    return creds

def select_tool(prompt_input: Callable = input) -> str:
    """
    Interactively select a supported tool.
    Args:
        prompt_input (Callable): Input function (default: input).
    Returns:
        str: Selected tool name.
    """
    print("Welcome to Digitalworks2020 DevOps CLI setup!")
    print("Supported tools:")
    for idx, tool in enumerate(SUPPORTED_TOOLS, 1):
        print(f"{idx}. {tool.capitalize()}")
    while True:
        choice = prompt_input("Select a tool by name: ").strip().lower()
        if choice in SUPPORTED_TOOLS:
            return choice
        print("Invalid choice. Please try again.")

def create_or_load_config(prompt_input: Callable = input) -> Tuple[Dict[str, Any], str, str]:
    """
    Create or load configuration, supporting multiple tools and accounts.
    Args:
        prompt_input (Callable): Input function (default: input).
    Returns:
        tuple: (config dict, selected tool, selected account name)
    """
    config: Dict[str, Any] = {}
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            config = json.load(f)
        # Ensure all supported tools are present in config
        for tool_name in SUPPORTED_TOOLS:
            if tool_name not in config:
                config[tool_name] = {"accounts": {}}
    else:
        config = {tool: {"accounts": {}} for tool in SUPPORTED_TOOLS}

    tool: str = select_tool(prompt_input=prompt_input)
    accounts: Dict[str, Dict[str, str]] = config.get(tool, {}).get("accounts", {})

    def handle_jira_cloud_account(account_name: str, creds: Dict[str, str]) -> Dict[str, str]:
        """Handle Jira Cloud-specific account setup."""
        default_project = prompt_input("Enter default Jira project key (or leave blank to skip): ").strip()
        if default_project:
            creds["default_project"] = default_project
        default_board = prompt_input("Enter default Jira board name (or leave blank to skip): ").strip()
        if default_board:
            creds["default_board"] = default_board
        return creds

    def handle_jira_server_account(account_name: str, creds: Dict[str, str]) -> Dict[str, str]:
        """Handle Jira Server-specific account setup."""
        default_project = prompt_input("Enter default Jira project key (or leave blank to skip): ").strip()
        if default_project:
            creds["default_project"] = default_project
        default_board = prompt_input("Enter default Jira board name (or leave blank to skip): ").strip()
        if default_board:
            creds["default_board"] = default_board
        return creds

    TOOL_ACCOUNT_HANDLERS: Dict[str, Callable[[str, Dict[str, str]], Dict[str, str]]] = {
        "jira_cloud": handle_jira_cloud_account,
        "jira_server": handle_jira_server_account,
        # Future: "aws": handle_aws_account, etc.
    }

    def add_account() -> None:
        account_name = prompt_input(f"Enter a unique {tool} account name: ").strip()
        if account_name in accounts:
            print("Account already exists. Please choose another name.")
            return
        creds = prompt_for_account(tool, account_name, prompt_input=prompt_input)
        handler = TOOL_ACCOUNT_HANDLERS.get(tool)
        if handler:
            creds = handler(account_name, creds)
        accounts[account_name] = creds
        config[tool]["accounts"] = accounts
        atomic_write_config(config)
        print(f"Account '{account_name}' added.")

    def delete_account() -> None:
        if not accounts:
            print("No accounts to delete.")
            return
        del_name = prompt_input("Enter the account name to delete: ").strip()
        if del_name in accounts:
            confirm = prompt_input(f"Are you sure you want to delete account '{del_name}'? (y/n): ").strip().lower()
            if confirm == "y":
                del accounts[del_name]
                config[tool]["accounts"] = accounts
                atomic_write_config(config)
                print(f"Account '{del_name}' deleted.")
            else:
                print("Deletion cancelled.")
        else:
            print("Account not found.")

    def list_accounts() -> None:
        print(f"\n{tool.capitalize()} Accounts:")
        if accounts:
            for idx, name in enumerate(accounts, 1):
                print(f"{idx}. {name}")
        else:
            print("No accounts found.")

    while True:
        list_accounts()
        choice = prompt_input(
            f"Choose an account by name, type 'add' to add a new {tool} account, or 'delete' to remove an account: "
        ).strip()
        if choice == "add":
            add_account()
        elif choice == "delete":
            delete_account()
        elif choice in accounts:
            print(f"Selected account: {choice}")
            return config, tool, choice
        else:
            print("Invalid choice. Please try again.")
