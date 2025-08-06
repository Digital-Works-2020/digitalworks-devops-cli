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
        if tool != "aws_sso":
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
                    # Segregate issues by status
                    status_map = {}
                    for issue in issues:
                        status = getattr(issue.fields, 'status', None)
                        status_name = status.name if status else "Unknown"
                        status_map.setdefault(status_name, []).append(issue)
                    print(f"\nYour issues in current sprint (segregated by status):")
                    for status_name, status_issues in status_map.items():
                        print(f"\nStatus: {status_name}")
                        for issue in status_issues:
                            print(f"- {issue.key}: {issue.fields.summary}")
                else:
                    print("No issues assigned to you in current sprint or error occurred.")
            elif op_choice == "3":
                stats, avg_velocity = client.get_sprint_story_points_stats(board_name)
                if stats:
                    print("\nStory Points for Last 3 Closed Sprints:")
                    for sprint_stat in stats:
                        print(f"Sprint: {sprint_stat['sprint']}")
                        print(f"  Committed SP: {sprint_stat['committed_sp']:.2f}")
                        print(f"  Achieved SP: {sprint_stat['achieved_sp']:.2f}")
                    print(f"Avg Achieved SP (last 3): {avg_velocity:.2f}")
                else:
                    print("No sprint stats available or error occurred.")
            else:
                print("Invalid operation choice.")

        # Tool dispatch
        if tool == "aws_sso":
            from devops_cli.aws_client import AWSClient
            print("\nAWS SSO integration. No credentials required; uses default AWS CLI profile.")
            profiles = AWSClient.list_profiles()
            if not profiles:
                print("No AWS CLI profiles found. Please configure AWS CLI first.")
                return
            print("Available AWS profiles:")
            for idx, prof in enumerate(profiles, 1):
                print(f"{idx}. {prof}")
            while True:
                prof_choice = prompt_input(f"Select a profile (1-{len(profiles)}): ").strip()
                if prof_choice.isdigit() and 1 <= int(prof_choice) <= len(profiles):
                    profile = profiles[int(prof_choice) - 1]
                    break
                print("Invalid choice. Please try again.")
            client = AWSClient(profile)
            if not client.check_credentials():
                AWSClient.sso_login(profile)
                client = AWSClient(profile)
            operations = __import__('devops_cli.config').config.TOOL_CONFIGS["aws_sso"].get('operations', [])
            print("\nSupported AWS SSO Operations:")
            for idx, op in enumerate(operations, 1):
                print(f"{idx}. {op['label']}")
            op_choice = prompt_input(f"Choose an operation (1-{len(operations)}): ").strip()
            from datetime import datetime
            now = datetime.utcnow()
            if op_choice == "1":
                cost = client.get_month_cost(now.year, now.month)
                if cost is not None:
                    print(f"Current month ({now.year}-{now.month:02d}) AWS cost: ${cost:.2f}")
                else:
                    print("Could not fetch current month cost.")
            elif op_choice == "2":
                prev_month = now.month - 1 if now.month > 1 else 12
                prev_year = now.year if now.month > 1 else now.year - 1
                cost = client.get_month_cost(prev_year, prev_month)
                if cost is not None:
                    print(f"Previous month ({prev_year}-{prev_month:02d}) AWS cost: ${cost:.2f}")
                else:
                    print("Could not fetch previous month cost.")
            else:
                print("Invalid operation choice.")
        elif tool == "jira_cloud":
            config, tool, account = create_or_load_config(prompt_input=prompt_input)
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
            config, tool, account = create_or_load_config(prompt_input=prompt_input)
            creds = config[tool]['accounts'][account]
            project_key = creds.get('default_project')
            board_name = creds.get('default_board')
            use_default_project = False
            use_default_board = False
            if project_key:
                use_default_project = prompt_input(f"Use default project '{project_key}'? (y/n): ").strip().lower() == "y"
            if not use_default_project:
                project_key = prompt_input("Enter Jira project key: ").strip()
            if board_name:
                use_default_board = prompt_input(f"Use default board '{board_name}'? (y/n): ").strip().lower() == "y"
            if not use_default_board:
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
