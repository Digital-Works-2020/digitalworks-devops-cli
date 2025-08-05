# digitalworks-devops-cli

A unified, modular CLI for DevOps operations across tools like Jira Cloud, Jira Server, AWS, and more. Built by Digitalworks2020.

## Features
- Modular architecture: Easily add integrations for new tools (Jira Cloud, Jira Server, AWS, etc.)
- User-driven, secure config creation at first run (multi-account, secure credentials)
- Scalable, reliable, and enterprise-ready structure
- Follows PEP8 and Codacy standards for maintainability
- Open source (MIT License) with required credits for commercialization

## Supported Tools
- Jira Cloud (multi-account, secure credentials, default project/board)
- Jira Server (multi-account, secure credentials, default project/board)
- Modular for future tools

## Configuration
Configuration is modular and supports multiple tools and accounts. Credentials are stored securely and you can set a default project/board for Jira Cloud and Jira Server accounts.

### Example Config
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
        "username": "user@company.com",
        "password": "...",
        "default_project": "ENT",
        "default_board": "Enterprise Board"
      }
    }
  }
}
```

## Getting Started
1. Clone the repo
2. Install dependencies
3. Run the CLI

## Coding Standards
- All code follows PEP8 and Codacy standards (typing, error handling, no debug prints in production)
- Modular, well-documented, and ready for enterprise use

## Credits
If you commercialize this project, you must give credit to Digitalworks2020.

## License
MIT
