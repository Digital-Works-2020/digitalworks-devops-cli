<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->


This project is a unified, modular DevOps CLI for Digitalworks2020, starting with Jira integration and designed for easy expansion (e.g., AWS, etc.).

**Design Principles:**
- Modular, scalable, reliable, and secure architecture.
- Each tool (Jira, AWS, etc.) is a separate module, with its own credential requirements and logic.
- User configuration is created and managed at runtime, supporting multiple accounts per tool.
- The CLI greets the user, lists supported tools, and guides them through interactive setup and account selection.
- Credentials are securely handled (e.g., API tokens via getpass).
- Configuration is written atomically for reliability.
- Follows PEP8 and Codacy standards for maintainability and code quality.


**Config Structure:**
- Uses a dictionary per tool, with an 'accounts' sub-dictionary for multiple account support.
- Each tool defines its credential fields in a central config (see TOOL_CONFIGS in config.py).
- JiraCloud and JiraServer are treated as separate tools (e.g., 'jira_cloud', 'jira_server'). Both support listing the current sprint name for a project/board using the python-jira module and OOP design. Pipfile includes `jira` as a requirement.
- Easily extendable: add new tools by updating SUPPORTED_TOOLS and TOOL_CONFIGS.

**User Experience:**
- CLI is interactive and user-friendly, with clear prompts and validation.
- Guides user through tool selection, account listing, credential entry, and allows users to delete accounts interactively.

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
