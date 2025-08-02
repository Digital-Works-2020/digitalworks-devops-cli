
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


TOOL_CONFIGS = {
    "jira_cloud": {
        "fields": [
            {"name": "url", "prompt": "Cloud URL", "secure": False},
            {"name": "username", "prompt": "Cloud username", "secure": False},
            {"name": "api_token", "prompt": "Cloud API token", "secure": True}
        ]
    },
    # Future: Add 'jira_server', 'aws', etc.
}

CONFIG_PATH = os.path.expanduser("~/.digitalworks_devops_cli_config.json")
SUPPORTED_TOOLS = ["jira_cloud"]  # Extendable for future tools

def atomic_write_config(config):
    """Atomically write config to disk."""
    temp_fd, temp_path = tempfile.mkstemp()
    with os.fdopen(temp_fd, 'w') as tmp_file:
        json.dump(config, tmp_file, indent=2)
    shutil.move(temp_path, CONFIG_PATH)

def prompt_for_account(tool, account_name, prompt_input=input):
    """Prompt user for account credentials for the given tool."""
    fields = TOOL_CONFIGS[tool]["fields"]
    creds = {}
    for field in fields:
        if field["secure"]:
            value = getpass.getpass(f"Enter {tool.replace('_', ' ').title()} {field['prompt']} for '{account_name}': ")
        else:
            value = prompt_input(f"Enter {tool.replace('_', ' ').title()} {field['prompt']} for '{account_name}': ").strip()
        creds[field["name"]] = value
    return creds

def select_tool(prompt_input=input):
    """Interactively select a supported tool."""
    print("Welcome to Digitalworks2020 DevOps CLI setup!")
    print("Supported tools:")
    for idx, tool in enumerate(SUPPORTED_TOOLS, 1):
        print(f"{idx}. {tool.capitalize()}")
    while True:
        choice = prompt_input("Select a tool by name: ").strip().lower()
        if choice in SUPPORTED_TOOLS:
            return choice
        print("Invalid choice. Please try again.")

def create_or_load_config(prompt_input=input):
    """Create or load configuration, supporting multiple tools and accounts."""
    config = {}
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            config = json.load(f)
    else:
        config = {tool: {"accounts": {}} for tool in SUPPORTED_TOOLS}

    tool = select_tool(prompt_input=prompt_input)
    accounts = config.get(tool, {}).get("accounts", {})
    while True:
        print(f"\n{tool.capitalize()} Accounts:")
        if accounts:
            for idx, name in enumerate(accounts, 1):
                print(f"{idx}. {name}")
        else:
            print("No accounts found.")

        choice = prompt_input(
            f"Choose an account by name, type 'add' to add a new {tool} account, or 'delete' to remove an account: "
        ).strip()
        if choice == "add":
            account_name = prompt_input(f"Enter a unique {tool} account name: ").strip()
            if account_name in accounts:
                print("Account already exists. Please choose another name.")
                continue
            creds = prompt_for_account(tool, account_name, prompt_input=prompt_input)
            accounts[account_name] = creds
            config[tool]["accounts"] = accounts
            atomic_write_config(config)
            print(f"Account '{account_name}' added.")
        elif choice == "delete":
            if not accounts:
                print("No accounts to delete.")
                continue
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
        elif choice in accounts:
            print(f"Selected account: {choice}")
            return config, tool, choice
        else:
            print("Invalid choice. Please try again.")
