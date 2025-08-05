"""
Main entry point for Digitalworks2020 DevOps CLI.
Follows PEP8 and Codacy standards.
"""

import sys
from devops_cli.config import create_or_load_config

def prompt_input(prompt):
    value = input(prompt)
    if value.strip().lower() == "exit":
        print("Exiting Digitalworks2020 DevOps CLI. Goodbye!")
        sys.exit(0)
    return value

def main():
    print("\nWelcome to Digitalworks2020 DevOps CLI!")
    while True:
        config, tool, account = create_or_load_config(prompt_input=prompt_input)
        print(f"\nSelected tool: {tool}")
        print(f"Selected account: {account}")
        # Hide secure fields when printing account details
        account_details = config[tool]['accounts'][account].copy()
        secure_fields = [f['name'] for f in __import__('devops_cli.config').config.TOOL_CONFIGS[tool]['fields'] if f['secure']]
        for field in account_details:
            if field in secure_fields:
                account_details[field] = "<hidden>"
        print(f"Account details: {account_details}")

        # Modular tool operation handling
        def handle_jira_cloud(creds, project_key, board_name):
            from devops_cli.jira_cloud import JiraCloudClient
            client = JiraCloudClient(
                creds['url'], creds['username'], creds['api_token']
            )
            sprint_name = client.get_current_sprint_name(project_key, board_name)
            if sprint_name:
                print(f"Current sprint for project '{project_key}': {sprint_name}")
            else:
                print(f"No active sprint found for project '{project_key}'.")

        def handle_jira_server(creds, project_key, board_name):
            from devops_cli.jira_server import JiraServerClient
            client = JiraServerClient(
                creds['url'], creds['api_token']
            )
            operations = __import__('devops_cli.config').config.TOOL_CONFIGS["jira_server"].get('operations', [])
            print(f"\nSupported Jira Server Operations:")
            for idx, op in enumerate(operations, 1):
                print(f"{idx}. {op['label']}")
            op_choice = prompt_input(f"Choose an operation (1-{len(operations)}): ").strip()
            if op_choice == "1":
                sprint_name = client.get_current_sprint_name(project_key, board_name)
                if sprint_name:
                    print(f"Current sprint for project '{project_key}': {sprint_name}")
                else:
                    print(f"No active sprint found for project '{project_key}'.")
            elif op_choice == "2":
                issues = client.get_my_issues_in_current_sprint(board_name)
                if issues:
                    print(f"\nYour issues in current sprint:")
                    for issue in issues:
                        print(f"- {issue.key}: {issue.fields.summary}")
                else:
                    print("No issues assigned to you in current sprint or error occurred.")
            else:
                print("Invalid operation choice.")

        # Tool dispatch
        if tool == "jira_cloud":
            creds = config[tool]['accounts'][account]
            project_key = creds.get('default_project')
            board_name = creds.get('default_board')
            use_default = False
            if project_key:
                use_default = prompt_input(f"Use default project '{project_key}'? (y/n): ").strip().lower() == "y"
            if not use_default:
                project_key = prompt_input("Enter Jira project key: ").strip()
            if not board_name:
                board_name = prompt_input("Enter Jira board name: ").strip()
            handle_jira_cloud(creds, project_key, board_name)
        elif tool == "jira_server":
            creds = config[tool]['accounts'][account]
            project_key = creds.get('default_project')
            board_name = creds.get('default_board')
            use_default = False
            if project_key:
                use_default = prompt_input(f"Use default project '{project_key}'? (y/n): ").strip().lower() == "y"
            if not use_default:
                project_key = prompt_input("Enter Jira project key: ").strip()
            if not board_name:
                board_name = prompt_input("Enter Jira board name: ").strip()
            while True:
                handle_jira_server(creds, project_key, board_name)
                next_action = prompt_input("\nPress Enter to perform another operation, type 'back' to select another tool, or 'exit' to quit: ").strip().lower()
                if next_action == "back":
                    break
                if next_action == "exit":
                    print("Exiting Digitalworks2020 DevOps CLI. Goodbye!")
                    sys.exit(0)
        else:
            prompt_input("\nPress Enter to continue or type 'exit' to quit: ")

if __name__ == "__main__":
    main()
