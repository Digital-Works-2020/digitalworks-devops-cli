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
        # Future: Add tool-specific operations here
        prompt_input("\nPress Enter to continue or type 'exit' to quit: ")

if __name__ == "__main__":
    main()
