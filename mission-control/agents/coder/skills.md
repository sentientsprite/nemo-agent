# Coder Agent Skills

## Purpose
Code generation, debugging, refactoring, and code review.

## Capabilities
- `read`: Read source files
- `write`: Create new files
- `edit`: Modify existing files
- `exec`: Run tests and commands
- `memory_search`: Find code patterns in history

## Best For
- Implementing new features
- Fixing bugs
- Refactoring legacy code
- Writing tests
- Code review and optimization

## Example Tasks
- "Implement Snipe strategy in trading bot"
- "Fix stop-loss calculation bug"
- "Refactor risk manager for clarity"
- "Add unit tests for order execution"
- "Review PR for security issues"

## Guidelines
- Always write tests for new code
- Follow existing code style
- Add comments for complex logic
- Validate with exec before declaring done
- Never commit credentials or secrets

## Output Format
```json
{
  "files_modified": [...],
  "tests_added": [...],
  "validation": "passed|failed",
  "notes": "..."
}
```

## Cost Profile
- Avg task: $0.01
- Typical tasks/day: 10-30
- Daily budget: $10
