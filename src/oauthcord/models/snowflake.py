"""Wrapper model for validated Discord snowflake identifiers."""

__all__ = ("Snowflake",)


class Snowflake:
    """Simple wrapper around a validated Discord snowflake ID."""

    def __init__(self, id: int | str) -> None:
        if not str(id).isdigit():
            raise ValueError(f"Expected a snowflake ID, got {id!r} instead.")

        self.id = int(id)
