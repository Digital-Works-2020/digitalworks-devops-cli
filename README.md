# digitalworks-devops-cli

A unified, modular CLI for DevOps operations across tools like Jira Cloud, Jira Server, AWS SSO, and more. Built by Digitalworks2020.

## Features
- **Highly modular architecture:** Each tool (Jira Cloud, Jira Server, AWS SSO, etc.) is a separate module with its own logic and configuration.
- **Stateless AWS SSO:** No account management for AWS SSO; directly lists AWS CLI profiles and allows profile switching at runtime.
- **Multi-account, secure config:** For tools like Jira, supports multiple accounts and secure credential storage.
- **Interactive, user-friendly CLI:** Menu-driven, guides user through tool selection, account selection (where applicable), and operations.
- **Extensible:** Add new tools by updating SUPPORTED_TOOLS and TOOL_CONFIGS in `config.py` and adding a new module.
- **Enterprise-ready:** Scalable, reliable, and follows PEP8 and Codacy standards.
- **Open source (MIT License):** Required credits for commercialization.

## Supported Tools
- **Jira Cloud:** Multi-account, secure credentials, default project/board, analytics.
- **Jira Server:** Multi-account, secure credentials, default project/board, analytics.
  - **Current Sprint Grouping:** Group current sprint issues by assignee and issue type
- **AWS SSO:** Stateless, no account management, profile-based, supports cost analytics and profile switching at runtime.
- **Modular for future tools:** Add new integrations easily.


## Usage & User Experience
- On first run, the CLI greets you and prompts for tool selection.
- For Jira tools, you can add, select, or delete accounts, and set defaults for project/board.
- For Jira Server, you can:
  - Display current sprint name
  - List your issues in the current sprint
  - Get story points for the last 3 closed sprints
  - Group current sprint issues by assignee and issue type

- For AWS SSO:
  - You select a profile from your AWS CLI config (no account management needed).
  - You can switch profiles or tools at any time.
  - For EC2 instance operations, you are prompted for the AWS region every time (region is not stored or defaulted).
- Each tool presents a menu of supported operations (e.g., analytics, cost, sprint info).
- All sensitive credentials are handled securely and never printed.

### Example Config (Jira tools)
```
{
  "jira_cloud": {
    "accounts": {
      "work": {
        "url": "https://yourdomain.atlassian.net",
        "username": "user@example.com",
        "api_token": "...",
        "default_project": "PROJ",
        "default_board": "Board Name"
      }
    }
  },
  "jira_server": {
    "accounts": {
      "enterprise": {
        "url": "https://jira.company.com",
        "api_token": "...",
        "default_project": "ENT",
        "default_board": "Enterprise Board"
      }
    }
  },
  "aws_sso": {}
}
```

## Getting Started
1. Clone the repo
2. Install dependencies (see Pipfile)
3. Run the CLI: `python -m devops_cli.main`

## Coding Standards
- All code follows PEP8 and Codacy standards (typing, error handling, no debug prints in production)
- Modular, well-documented, and ready for enterprise use

## Credits
If you commercialize this project, you must give credit to Digitalworks2020.

## License
MIT
