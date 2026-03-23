__all__ = ("Snowflake",)


class Snowflake:
    def __init__(self, id: int | str) -> None:
        if not str(id).isdigit():
            raise ValueError(f"Expected a snowflake ID, got {id!r} instead.")

        self.id = int(id)
