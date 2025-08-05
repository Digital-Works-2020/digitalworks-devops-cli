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

        # Jira Cloud: List current sprint name
        if tool == "jira_cloud":
            from devops_cli.jira_cloud import JiraCloudClient
            creds = config[tool]['accounts'][account]
            client = JiraCloudClient(
                creds['url'], creds['username'], creds['api_token']
            )
            project_key = creds.get('default_project')
            board_name = creds.get('default_board')
            use_default = False
            if project_key:
                use_default = prompt_input(f"Use default project '{project_key}'? (y/n): ").strip().lower() == "y"
            if not use_default:
                project_key = prompt_input("Enter Jira project key: ").strip()
            if not board_name:
                board_name = prompt_input("Enter Jira board name: ").strip()
            sprint_name = client.get_current_sprint_name(project_key, board_name)
            if sprint_name:
                print(f"Current sprint for project '{project_key}': {sprint_name}")
            else:
                print(f"No active sprint found for project '{project_key}'.")
        # Jira Server: Supported operations menu from config
        elif tool == "jira_server":
            from devops_cli.jira_server import JiraServerClient
            creds = config[tool]['accounts'][account]
            client = JiraServerClient(
                creds['url'], creds['api_token']
            )
            project_key = creds.get('default_project')
            board_name = creds.get('default_board')
            use_default = False
            if project_key:
                use_default = prompt_input(f"Use default project '{project_key}'? (y/n): ").strip().lower() == "y"
            if not use_default:
                project_key = prompt_input("Enter Jira project key: ").strip()
            if not board_name:
                board_name = prompt_input("Enter Jira board name: ").strip()

            operations = __import__('devops_cli.config').config.TOOL_CONFIGS[tool].get('operations', [])
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
        prompt_input("\nPress Enter to continue or type 'exit' to quit: ")

if __name__ == "__main__":
    main()
