<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->



This project is a unified, modular DevOps CLI for Digitalworks2020, supporting Jira Cloud, Jira Server, AWS SSO, and designed for easy expansion (e.g., more tools).

**Design Principles:**
- Modular, scalable, reliable, and secure architecture.
- Each tool (Jira, AWS SSO, etc.) is a separate module, with its own credential requirements and logic.
- User configuration is created and managed at runtime, supporting multiple accounts per tool (except AWS SSO, which is stateless).
- The CLI greets the user, lists supported tools, and guides them through interactive setup and account/profile selection.
- Credentials are securely handled (e.g., API tokens via getpass).
- Configuration is written atomically for reliability.
- Follows PEP8 and Codacy standards for maintainability and code quality.
- Each tool's main logic is implemented in its own function for maintainability and extensibility.

**Config Structure:**
- Jira Server supports grouping current sprint issues by assignee and issue type 

**User Experience:**
- For Jira Server, the menu includes an option to group current sprint issues by assignee and issue type

**Licensing:**
- Open source (MIT). Credits to Digitalworks2020 required for commercialization.

**Roles:**
- You are expected to act as developer, architect, tester, and UX designer to ensure the project is robust and maintainable.

**Folder Structure:**
- Source code is in `devops_cli/`.
- Config and instructions are in `.github/` and root files.
- Use `.gitignore` to exclude config, environment, and build artifacts.

**Best Practices:**
- All code and tests should be well-documented, modular, and follow PEP8 and Codacy standards (typing, error handling, no debug prints in production code).
- Use clear docstrings for all public classes and methods.
- Avoid debug prints; use logging if needed for enterprise code.
- Keep copilot-instructions.md updated with any major architectural, config, or folder structure changes.
