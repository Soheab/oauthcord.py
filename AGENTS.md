# AGENTS

Repository-wide instructions for AI assistants working on this project.

## Project overview
- This repository is a Discord OAuth2 API wrapper.

## References
Use these sources for API behavior, payload shapes, and field semantics:

1. Unofficial docs (preferred): https://docs.discord.food/
2. Official docs: https://discord.com/developers/docs

If the sources disagree, follow the official Discord documentation.

## General rules
- Keep models, payload `TypedDict`s, and parsing logic in sync.
- Prefer strong, explicit typing and avoid duplication.
- Do not invent undocumented fields. If a field is used but undocumented, label it as such.
- Preserve public API compatibility. If renaming or removing public classes, provide aliases or update all callers.
- Use the minimum Python version from `.python-version` or `pyproject.toml`.
- Prefer modern language features; do not add backward-compatibility shims.
- Run project tooling via `uv run`.

## Typing and payload conventions
- Prefer `TypedDict` payloads and use `NotRequired` for optional keys.
- Every request payload passed as `params`, `data`, or `json` must have a matching `TypedDict` whose name ends with `Request`.
- Every response payload `TypedDict` must end with `Response`.
- Avoid no-op payload subclasses. If a subtype adds no fields, use an alias instead.
  Example: `SpecificPayload = BasePayload`
- Avoid `Any` unless the data is genuinely unstructured.
- Do not use `typing.cast`. Fix types at the source with better annotations, narrowing, overloads, or helper types.
- For model parsing, use `convert_snowflake`, `iso_to_datetime`, and `maybe_available` from `utils` where appropriate.
- Do not add ad hoc standalone helper functions for one-off serialization or coercion logic. Prefer shared utilities, model methods, or method-local logic unless the helper is broadly reusable.
- Use walrus assignment for mapping lookups when it improves clarity, for example `if (value := data.get("key")) is not None:`.
- Prefer `edit_*` method names over `modify_*` for library methods.
  `Modify*` type and payload names are acceptable when they mirror Discord API terminology.
- When a method accepts enum or flags models, also accept raw serialized values.
  Use unions such as `MyIntEnum | int`, `MyStrEnum | str`, and `MyFlags | int`.
- If an integer field has known literal values from docs or from inline comments,
  create an enum for model attributes and parsing logic. Keep payload `TypedDict`
  files as raw serialized types, such as a commented `Literal[...]`, instead of
  importing the public enum into `_types` files.
- If typing or linting becomes noisy on a specific line, use targeted ignores such as `# pyright: ignore[...]` or `# noqa: ...`.

## Model and `__slots__` rules
- Define `__slots__` for all models and keep them synchronized with the actual attributes.
- If a model has no attributes, use `__slots__ = ()`.
- If a model has attributes but no `__slots__`, add `__slots__`.
- If `__slots__` and attributes do not match, update `__slots__` to match.
- If a model has `__slots__` but no attributes, either remove `__slots__` or add the missing attributes.

Validate slot usage with:
- `uv run python scripts/check_slots_decorator_usage.py`
- `uv run python scripts/check_model_slots.py`

## Linting, formatting, and type checks
For touched Python files, keep Ruff normalization and type checking in this order:

1. `uv run ruff check . --select I --select RUF --fix --unsafe-fixes`
2. `uv run ruff check . --fix --unsafe-fixes`
3. `uv run ruff format .`
4. `uv run pyright`

OR just run `uv scripts/check.py` to do everything at once.

Notes:
- `ruff format` does not sort imports or `__all__`.
- All changes must pass `uv run pyright`.

## Docstrings
Apply docstrings to public API only.

- Use NumPy-style docstrings for public classes, methods, and functions.
- Keep descriptions concise, grammatical, and focused on behavior or important constraints.
- Include only relevant sections.
- Keep prose types aligned with type annotations.
- Do not document private members with leading `_` unless they are effectively public API or need maintainer-facing behavior notes.

Parameter style:
- Format each parameter as `name: :class:`type`` or `name: :func:`type``, followed by a concise description.
- If the type is `None` or a literal, do not wrap it in `:class:` or `:func:`.
- When referring to the `None` type, always write `:data:`None``.

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
