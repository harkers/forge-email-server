# Planner Agent Examples

## Example: feature decomposition

Goal:
- add a new admin workflow

Useful plan shape:
- task 1: map affected files and boundaries
- task 2: implement backend/API changes
- task 3: implement UI changes
- task 4: add validation/tests/docs
- task 5: review and acceptance

Each task should name:
- owner
- allowed scope
- expected outputs
- validation

## Anti-pattern
Do not split work into tiny units with no clear ownership benefit.
