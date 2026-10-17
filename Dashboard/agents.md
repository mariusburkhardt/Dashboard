# Development Guidelines

## Language and naming

- Use English for Python identifiers and German for user-facing interface text.
- Write comments and docstrings in German when clarification is needed.
- Use `snake_case` for functions and variables and `PascalCase` for classes.

## Quality

- Follow PEP 8 and add type hints to application code.
- Keep responsibilities in the domain, service, repository, controller, view,
  and application layers.
- Use the Python standard library for runtime functionality unless a dependency
  is justified.
- Validate domain input and surface unexpected errors rather than hiding them.

## Documentation and tests

- Keep the README and architecture diagram aligned with code changes.
- Add or update focused unit tests for changed behavior.
- Run the relevant tests with `python -m pytest -q`.
