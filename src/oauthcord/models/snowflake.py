__all__ = ("Snowflake",)


class Snowflake:
    def __init__(self, id: int | str) -> None:
        self.id = int(id)
