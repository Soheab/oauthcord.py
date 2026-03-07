# AGENTS

Repository-wide instructions for any AI assistant working on this project.

## Project overview
- This repository is a Discord OAuth2 API wrapper.

## Source of truth
Use these references for API behavior, payload shapes, and field semantics. If sources disagree, follow the official Discord documentation.

- Official docs: https://discord.com/developers/docs
- Community docs (useful detail): https://docs.discord.food/
- Discord Support Center: https://support.discord.com/hc/en-us

## Core engineering rules
- Keep models, payload `TypedDict`s, and parsing logic in sync.
- Prefer strong, explicit typing and avoid duplication.
- Do not invent undocumented fields; label them as undocumented when needed.
- Preserve public API compatibility. If renaming/removing public classes, provide aliases or update all callers.

## Python, typing, and payload conventions
- Use the repository minimum Python version from `pyproject.toml` (currently Python 3.14).
- Prefer modern language features; do not add backward-compatibility shims.
- Run all tools via `uv run`.
- Prefer `TypedDict` payloads with `NotRequired` for optional keys.
- Avoid no-op payload subclasses. If a subtype adds no fields, use an alias instead.
  - Example: `SpecificPayload = BasePayload`
- Any request payload (`params`, `data`, `json`) must have a matching `TypedDict` ending in `Request`.
- Any response payload `TypedDict` must end in `Response`.
- Avoid `Any` unless data is genuinely unstructured.
- In model parsing, use `convert_snowflake`, `iso_to_datetime`, and `maybe_available` from `utils` where appropriate.
- Keep model `__slots__` declarations accurate and synchronized with attributes.
- Use walrus assignment for mapping lookups when it improves clarity, e.g.:
  - `if (value := data.get("key")) is not None:`
- For library methods, prefer `edit_*` naming over `modify_*`.
  - `Modify*` type/payload names are acceptable when they mirror API terminology.
- If strict typing/linting becomes noisy on a specific line, use targeted ignores:
  - `# pyright: ignore[...]`
  - `# noqa: ...`

## Slots and model decorator rules
- Use `@(Stateless)BaseModel.add_slots(...)` only for classes inheriting from `(Stateless)BaseModel`.
- For non-`(Stateless)BaseModel` classes, define `__slots__` manually.

Validate with:
- `uv run python scripts/check_slots_decorator_usage.py`
- `uv run python scripts/check_model_slots.py`

## Linting, formatting, and type checks
Run these after changes (and when task checks require):

- `ruff format` does not sort imports or `__all__`. For import and `__all__` sorting, run `uv run ruff check . --select I --select RUF --fix --unsafe-fixes` before formatting.
- Keep touched Python files fully Ruff-normalized by running, in order: `uv run ruff check . --select I --select RUF --fix --unsafe-fixes`, `uv run ruff check . --fix --unsafe-fixes`, then `uv run ruff format .`.

- Import and `__all__` sorting: `uv run ruff check . --select I --select RUF --fix --unsafe-fixes`
- Lint + autofix: `uv run ruff check . --fix --unsafe-fixes`
- Format: `uv run ruff format .`
- Type check: `uv run pyright`

All changes must pass `uv run pyright`.

## Docstring standards
Apply docstrings to public API only.

- Use NumPy-style docstrings for public classes, methods, and functions.
- Write concise, grammatical descriptions.
- Document behavior and important constraints; avoid boilerplate.
- Include only relevant sections (omit empty/inapplicable sections).
- Keep prose types aligned with type annotations.
- Do not document private members (leading `_`) unless they are effectively public API or require maintainer-facing behavior notes.

Parameter style:
- Format each parameter as `name: :class:`type`` (or `:func:`type`` where appropriate), followed by a concise description.
- If the type is `None` or a literal, no `:class:`/`:func:` wrapper is required.

Function template:

```python
"""Short description.

Parameters
----------
name: :class:`type`
    Description.

Returns
-------
type
    Description.
"""
```

Class template:

```python
class ClassName:
    """Short description.

    Parameters
    ----------
    parameter_name: :class:`type`
        Description.

    Attributes
    ----------
    attribute_name: :class:`type`
        Description.
    """
```
