# git-msg

Analyze the current staged changes (or the changes described by the user) and produce a properly formatted semantic commit message that is as verbose and detailed as possible.

## Commit Message Format

```
<type>(<scope>): <subject>

[body]

[optional footer(s)]
```

- `<scope>` is optional
- `<subject>` must be written in **imperative mood, present tense** (e.g. `add` not `adds` or `added`)
- Separate the body from the subject with a blank line
- The body is **mandatory** — always include it, no matter how small the change
- Use the body to explain **what changed, why it changed, and what the before/after behavior is**
- List every file or module touched, and describe the specific change made in each
- For breaking changes, append `!` after the type/scope and add a `BREAKING CHANGE:` footer

## Breaking Changes

```
feat(api)!: remove deprecated user endpoint

BREAKING CHANGE: The /api/v1/users endpoint has been removed. Use /api/v2/users instead.
```

## Valid Types

| Type       | When to use | Example |
|------------|-------------|---------|
| `feat`     | A new feature for the user (not a build script feature) | `feat(checkout): add promo code support` |
| `fix`      | A bug fix for the user (not a build script fix) | `fix(auth): resolve token expiry edge case` |
| `docs`     | Changes to documentation only | `docs(readme): update installation instructions` |
| `style`    | Formatting, missing semicolons, whitespace — no logic change | `style: remove trailing whitespace` |
| `refactor` | Refactoring production code (e.g. renaming a variable) — no feature or fix | `refactor(api): rename getUserData to fetchUser` |
| `perf`     | Performance improvements | `perf(db): add index to speed up user queries` |
| `test`     | Adding or refactoring tests — no production code change | `test(cart): add unit tests for discount logic` |
| `chore`    | Updating build tasks, package manager configs, etc. — no production code change | `chore: bump eslint to v9` |
| `ci`       | Changes to CI configuration files or scripts (e.g. GitHub Actions, CircleCI, pipelines) | `ci(deploy): update production release pipeline` |

## Instructions

1. Look at the diff or the user's description of what changed.
2. If the diff spans multiple unrelated concerns, flag this and suggest splitting into separate commits, offering a message for each before proceeding.
3. Choose the **most appropriate type** from the table above.
4. Include a **scope** in parentheses if the change is clearly scoped to a module, component, or file area (e.g. `auth`, `api`, `readme`, `cart`). Omit scope if the change is broad.
5. Write a clear subject in **imperative mood** — what does this commit do? (e.g. `add`, not `adds` or `added`). The subject must be specific and descriptive enough that a developer can understand the change without reading the body.
6. **Always write a body**, even for small or single-line changes. The body must:
   - List **every file changed**, with a brief description of what was modified in each (e.g. `- src/auth/token.ts: extend expiry check to handle null refresh tokens`)
   - Explain **what** the change does and **why** it was necessary
   - Describe the **before/after behavior** where applicable (e.g. `Previously, the function returned undefined when X; it now returns Y`)
   - Call out any non-obvious decisions, trade-offs, or context a future developer would need to understand the change
   - Use bullet points (`-`) for per-file or per-concern breakdowns; use prose paragraphs for overall motivation and context
7. If the commit introduces a breaking change, append `!` to the type/scope and include a `BREAKING CHANGE:` footer describing the impact on consumers and any migration steps required.
8. Output **only the commit message** (no explanation unless the user asks), ready to copy-paste.
9. If the user asks for a draft, prepend `Draft:` to the full commit message (e.g. `Draft: feat(auth): add OAuth2 login flow`).

## Example of a Verbose Commit Message

```
fix(auth): resolve null reference error when refresh token is missing

Previously, the token refresh handler assumed a refresh token was always
present in the session object. If a user's session was created before
refresh tokens were introduced, or if the token had been manually cleared,
calling refreshAccessToken() would throw an uncaught TypeError at runtime,
logging the user out unexpectedly.

This fix adds a null/undefined guard before accessing the refresh token,
falling back to a re-authentication prompt instead of crashing.

Changes by file:
- src/auth/tokenService.ts: add null check on `session.refreshToken` before
  calling `refreshAccessToken()`; return early with `AUTH_REQUIRED` error
  code if token is absent
- src/auth/tokenService.test.ts: add test cases for missing refresh token
  scenario — covers null, undefined, and empty string values
- src/constants/errorCodes.ts: add new `AUTH_REQUIRED` error code used by
  the updated token service

No changes to the public API surface. This is a purely defensive fix with
no behavioral change for sessions that have a valid refresh token.
```
