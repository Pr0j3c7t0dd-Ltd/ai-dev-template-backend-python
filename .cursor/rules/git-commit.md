Rule Name: git-commit-message-best-practices
Description: Enforce best practices for writing git commit messages, inspired by Equal Experts' "Writing commit messages that tell a story".

# Git Commit Message Best Practices

## 1. Tell a Story
- Write commit messages that explain the "why" and "what" of the change, not just the "how".
- Provide context for future readers to understand the reason behind the change.

## 2. Use the Imperative Mood
- Start the subject line with a verb in the imperative mood (e.g., "Add", "Fix", "Update", "Remove").

## 3. Keep Subject Line Concise
- Limit the subject line to 50 characters or less.
- Capitalize the first letter.
- Do not end the subject line with a period.

## 4. Separate Subject from Body
- Leave a blank line between the subject and the body (if a body is needed).

## 5. Provide a Detailed Body (if necessary)
- Use the body to explain what and why vs. how.
- Wrap lines at 72 characters.
- Reference relevant issues, tickets, or context.

## 6. Make Each Commit a Logical Unit
- Each commit should represent a single logical change.
- Avoid mixing unrelated changes in one commit.

## 7. Use Consistent Formatting
- Use present tense and imperative mood throughout.
- Example: "Refactor authentication logic to improve clarity."

## 8. Avoid WIP and Non-descriptive Messages
- Do not use "WIP", "fix", "update", or similar vague messages.
- Be specific about what was changed and why.

## 9. Review Before Committing
- Reread your commit message before pushing to ensure clarity and completeness.

## 10. Example of A Good Commit Message

```
feat: implement dark mode toggle

Added a dark mode toggle button to the settings page. The feature uses
CSS variables to switch themes and persists the user’s preference in
localStorage. Includes unit tests for theme switching logic.
Closes #789.

- Updated `styles.css` with new theme variables
- Added `themeToggle.js` for handling user interactions
- Modified `settings.html` to include toggle UI
```

---

References:
- [Writing commit messages that tell a story (Equal Experts)](https://equalexperts.blogin.co/posts/writing-commit-messages-that-tell-a-story-289774)
