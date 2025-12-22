---
description: Generate professional Python documentation following specific styles (Google, NumPy, reST, GitHub).
---

This workflow guides you through generating standardized Python documentation with fine-grained control via parameters.

### 1. Parameters & Usage

Trigger this workflow using the following format:
`/document-python-projects docstring_style::"Google|NumPy|reST|GitHub" examples_in_docstrings::true|false max_line_length::120 additional_instructions::"Notes"`

| Parameter                 | Description                          | Default      |
| :------------------------ | :----------------------------------- | :----------- |
| `target_file_name`        | The file to document.                | Current File |
| `docstring_style`         | Google, NumPy, reST, or GitHub.      | Google       |
| `examples_in_docstrings`  | Include code examples in docstrings? | false        |
| `max_line_length`         | Maximum characters per line.         | 120          |
| `min_line_length`         | Minimum line length threshold.       | 80           |
| `additional_instructions` | Optional project-specific rules.     | -            |

#### ADDITIONAL BEHAVIOR IF PARAMETER MISSING:

- If target_file_name is not provided, use the current active file (@CurrentFile).
- If Docstring_Style is not provided, use "Google".
- If examples_in_docstrings is not provided, default to false (no examples in docstrings).
- If max_line_length or min_line_length are not provided, use defaults (120 and 80 respectively).
- If additional_instructions are provided, incorporate them as long as they do not conflict with constraints.

### 2. Task Definition

Document the file `{{{ target_file_name }}}` using the specified `{{{ docstring_style }}}` style:

1.  **Module Summary**: Add a docstring at the top summarizing the module's purpose and key responsibilities.
2.  **Member Documentation**: For each public class, method, and function, provide a docstring with:
    - A one-line summary (imperative mood).
    - A detailed description (when non-trivial).
    - Sections for **Parameters**, **Returns/Yields**, and **Raises**.
    - **Examples**: Include blocks ONLY if `{{{ examples_in_docstrings }}}` is true.
3.  **API Consistency**: Document constants and module-level variables only if they are part of the public API and their meaning is non-obvious.
4.  **Integrity**: Preserve all original code logic, signatures, and structure.

### 3. Core Constraints & Requirements

Ensure documentation meets these mandatory standards:

1.  **Module-Level Summary**: Every file must start with a summary of its purpose, responsibilities, and key objects.
2.  **Public API Focus**: Document all public classes, methods, and functions. Skip magic methods (e.g., `__init__`) unless they have non-trivial logic.
3.  **Docstring Content**:
    - One-line summary in imperative mood.
    - Detailed description for non-trivial logic.
    - Sections for **Parameters**, **Returns/Yields**, and **Raises**.
    - **Examples**: Include ONLY if `examples_in_docstrings` is true.
4.  **Formatting**:
    - **Line Length**: Respect `max_line_length`. Wrap text for readability.
    - **PEP 257**: Maintain consistency in spacing and structure.
    - **Class Attributes**: Document in the class-level docstring; avoid per-attribute docstrings in the body.
5.  **Type Inference**: Infer from usage or annotations. When uncertain, use generic types or omit; do not guess incorrectly.
6.  **Preserve Code**: NEVER modify logic, signatures, or existing imports.

### 3. Style Reference

### DOCSTRING STYLE REFERENCE/EXAMPLES:

Follow the headings and structure exactly as specified by the chosen style:

#### Google Style Example:

```python
def function_name(param1, param2):
    """Function description.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Description of return value.

    Raises:
        ExceptionType: Description of when exception is raised.

    Examples:  # (Only add this Examples section if examples_in_docstrings is true)
        >>> result = function_name("value1", "value2")
        >>> print(result)
        expected_output
    """
    ...
```

#### GitHub Style Example for Python:

````python
def function_name(param1, param2):
    """Function description.

    This function does something useful.

    ## Parameters

    * `param1` - Description of the first parameter
    * `param2` - Description of the second parameter

    ## Returns

    * Description of the return value

    ## Raises

    * `ExceptionType`: Description of when exception is raised

    ## Examples  # (Only add this Examples section if examples_in_docstrings is true)

    ```python
    result = function_name("value1", "value2")
    print(result)  # expected_output
    ```
    """
    ...
````

#### NumPy Style Example:

```python
def function_name(param1, param2):
    """Function description.

    This function does something useful with detailed explanation.

    Parameters
    ----------
    param1 : type
        Description of param1.
    param2 : type
        Description of param2.

    Returns
    -------
    type
        Description of return value.

    Raises
    ------
    ExceptionType
        Description of when exception is raised.

    Examples  # (Only add this Examples section if examples_in_docstrings is true)
    --------
    >>> result = function_name("value1", "value2")
    >>> print(result)
    expected_output
    """
    ...
```

#### reST Style Example:

```python
def function_name(param1, param2):
    """Function description.

    This function does something useful with detailed explanation.

    :param param1: Description of param1.
    :type param1: type
    :param param2: Description of param2.
    :type param2: type
    :returns: Description of return value.
    :rtype: type
    :raises ExceptionType: Description of when exception is raised.

    .. note::
        Additional notes or information about usage.

    .. code-block:: python  # (Only add this example section if examples_in_docstrings is true)

        # Example usage
        result = function_name("value1", "value2")
        print(result)  # expected_output
    """
    ...
```

### 5. OUTPUT_FORMAT:

- Output the fully documented version of the target file, preserving original code and structure.
- Place a brief module summary at the very top before any imports or code (module docstring).
- Ensure all public methods/functions/classes are documented according to the chosen style.
- Include example blocks in docstrings ONLY when {{{ examples_in_docstrings }}} is true, following the style-specific format.
- Use clear, consistent English.
- Wrap documentation lines to not exceed {{{ max_line_length }}}.
- Avoid unnecessary verbosity; prioritize precision and usefulness.
- If assumptions were necessary, include a short "Notes" section within the relevant docstring.
- When examples are included, ensure they are executable, meaningful, and demonstrate typical use cases.

### 6. QUALITY CHECKLIST:

- [ ] Module-level docstring present and concise.
- [ ] All public classes/functions/methods documented.
- [ ] Correct headings and structure for the selected style.
- [ ] Parameters, Returns/Yields, Raises are accurate and complete.
- [ ] Examples section included ONLY when examples_in_docstrings={{{ examples_in_docstrings }}} is true.
- [ ] If examples are included: they are meaningful, executable, and follow the style-specific format.
- [ ] No line exceeds max_line_length={{{ max_line_length }}}; lines are readable and generally meet min_line_length={{{ min_line_length }}} where natural.
- [ ] No per-attribute docstrings inside classes; attributes documented in class docstring if needed.
- [ ] No code changes, only documentation added.
- [ ] Ambiguities labeled as notes; no fabricated specifics.
- [ ] Example blocks (when present) demonstrate typical usage patterns and add value beyond the description.