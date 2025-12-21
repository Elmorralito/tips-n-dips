---
description: Automatically discover and document all Python files in the workspace using /document-python-projects.
---

This workflow orchestrates the sequential documentation of an entire Python project. It ensures high-quality mass documentation by managing discovery, exclusion logic, and strict context management.

### 1. Parameters & Usage

Trigger this workflow using:
`/batch-document-python-workspace workspace_root::"." docstring_style::"Google" batch_size::5 exclude_patterns::"venv/*,tests/*"`

| Parameter                 | Description                                            | Default                |
| :------------------------ | :----------------------------------------------------- | :--------------------- |
| `workspace_root`          | Root directory to scan for Python files.               | `{{ @WorkspaceRoot }}` |
| `docstring_style`         | Google, NumPy, reST, or GitHub.                        | Google                 |
| `examples_in_docstrings`  | Include code examples in docstrings?                   | false                  |
| `max_line_length`         | Maximum characters allowed per documentation line.     | 120                    |
| `exclude_patterns`        | Comma-separated patterns (e.g., `venv/*,env/*`).       | `venv/*,.git/*`        |
| `batch_size`              | Number of files to process before clearing context.    | 5                      |
| `include_private_modules` | Document files starting with `_`?                      | false                  |
| `create_summary`          | Generate a `DOCUMENTATION_SUMMARY.md` at project root? | true                   |

### 2. Task Definition

Execute a robust batch documentation process for `{{{ workspace_root }}}` using these phases:

#### Phase 1: Discovery

1.  **Scan**: Recursively find all `.py` files in `{{{ workspace_root }}}`.
2.  **Filter**: Apply `{{{ exclude_patterns }}}`, `.gitignore` rules, and `{{{ include_private_modules }}}`.
3.  **Sort**: Order files by directory depth (leaf modules first) or project structure.
4.  **Confirm**: **MUST** display the list of discovered files and wait for user confirmation before proceeding.

#### Phase 2: Batch Execution

For each discovered Python file:

1.  **Check Coverage**: Skip files that are already "well-documented" (>70% coverage with module docstrings) unless re-documentation is requested.
2.  **Process**: Invoke the engine workflow via:
    `/document-python-projects target_file_name::"{file_path}" docstring_style::"{{{ docstring_style }}}" examples_in_docstrings::{{{ examples_in_docstrings }}} max_line_length::{{{ max_line_length }}}`
3.  **Sequential Flow**: Wait for the current file to be completely documented before starting the next.
4.  **Monitor**: display progress tracker (e.g., "Processed X/Y files...").

#### Phase 3: Reporting

If `{{{ create_summary }}}` is true:

1.  Generate `DOCUMENTATION_SUMMARY.md` in the workspace root.
2.  Include: Success/Skip/Fail statistics, style used, configuration, and lists of processed/failed files.

### 4. Context Management Strategy

Manage context and memory usage efficiently to handle large workspaces:

- **Before processing**: Load only the workflow instructions, file discovery list, and parameters.
- **During processing**:
  - Load only the current file to be documented.
  - Invoke `/document-python-projects`.
  - Wait for documentation completion.
  - Log results immediately.
- **After every `{{{ batch_size }}}` files**: Perform a **Context Reset**. Clear all processed file contents and command output logs.
- **Retain Always**: Tracking state (index, counts), the original discovery list, and this workflow's global state.
- **Completion**: Clear all file contents and display/save the final summary report.

### 5. Error Handling

Ensure robustness and traceability across mass documentation:

- **Non-Critical Errors**: Log the issue and **CONTINUE** with the next file.
  - **Syntax Errors**: Log as failure; skip documentation for that file.
  - **Permission/Access**: Log as failure; skip.
  - **Command Timeout**: Skip after 60s; log as timeout.
  - **Invocation Failure**: Log command error; proceed.
- **Critical Errors**: Halt only for system-level failures (e.g., loss of workspace access). Save a partial `DOCUMENTATION_SUMMARY.md` before exiting.
- **Graceful Termination**: If the user cancels, save the current progress report to avoid data loss.

Ensure the process adheres to these detailed standards:

**Workflow Execution:**

1.  **Strict Orchestration**: NEVER attempt to document files directly. **MUST** use the `/document-python-projects` command.
2.  **Sequential Processing**: Process files strictly one at a time to ensure quality and avoid context overflow.
3.  **User Guardrail**: Never begin processing without showing the discovery list and receiving confirmation.
4.  **Error Handling**: If a file fails, log the error and continue. Do not halt the entire batch.
5.  **Context Management**: **CRITICAL:** Every `{{{ batch_size }}}` files, explicitly clear the context window, retaining only the global execution state and file list.

**Integrity & Quality:** 6. **No Logic Changes**: Preserve all original code functionality, signatures, and imports. 7. **Relative Pathing**: Use relative paths from the workspace root for all file references in summaries and logs. 8. **Large Workspace Warning**: If >100 files are discovered, warn the user and recommend processing subdirectories separately. 9. **Standard Consistency**: Maintain the chosen `{{{ docstring_style }}}` consistently across the entire workspace.

**QUALITY CHECKLIST:**
- [ ] All Python files in workspace discovered correctly
- [ ] Exclusion patterns applied properly
- [ ] Files processed in logical order (dependencies first when possible)
- [ ] /document-python-projects command invoked explicitly for each file
- [ ] Command invocation syntax is correct and includes all parameters
- [ ] Context cleared every {batch_size} files
- [ ] Progress displayed clearly during processing
- [ ] Errors logged without halting entire process
- [ ] Summary report generated with accurate statistics (if enabled)
- [ ] All documented files maintain consistent style
- [ ] No code functionality changed
- [ ] Original file structure preserved
- [ ] Execution time reasonable for workspace size
- [ ] User confirmation requested before processing
- [ ] Large workspace warnings displayed appropriately

**NOTES:**
- For very large workspaces (>100 files), consider running on subdirectories
- The command will ask for confirmation before processing
- Already well-documented files are skipped by default to save time
- Context clearing ensures the command can handle projects of any size
- The summary report is saved as `DOCUMENTATION_SUMMARY.md` in workspace root (or subdirectory if workspace_root is specified)
- Each file is processed independently - failures don't affect other files
- The command explicitly invokes `/document-python-projects` for each file to ensure consistent documentation quality
