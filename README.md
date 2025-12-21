# tips-dips

Repository containing tips and dips gathered along the way.

## Useful toolkits for AI-Supported IDEs

### [`Antigravity Agent`](https://antigravity.google/docs/agent)

This project utilizes the Antigravity Agent for AI-assisted development. Configuration and custom behavior are defined in:

- [`.agent/rules`](file:///.agent/rules): Contains context-specific rules and coding standards for the agent.
- [`.agent/workflows`](file:///.agent/workflows): Contains pre-defined multi-step workflows (slash commands) for common tasks.

For setting up the agent globally, set the directory .gemini/{rules, workflows, ...} at the $HOME or user's home directory.

### [`Cursor`](https://cursor.com/docs)

This project utilizes the Cursor AI IDE for AI-assisted development. Configuration and custom behavior are defined in:

- [`.cursor/rules`](file:///.cursor/rules): Contains custom Cursor extensions and settings.
- [`.cursor/commands`](file:///.cursor/commands): Contains custom prompt files and commands for Cursor.

For setting up the cursor globally, set the directory .cursor/{rules, commands, ...} at the $HOME or user's home directory.
