# Antigravity Rules for Gadget Deluxe Shop

## Git Workflow
- Whenever you make code, template, configuration, or database migration changes according to user commands, automatically run:
  1. `git add -A`
  2. `git commit -m "<concise descriptive message>"`
  3. `git push origin main`
- Always verify tests pass (`.\venv\Scripts\python manage.py test`) before pushing when functional code has changed.
