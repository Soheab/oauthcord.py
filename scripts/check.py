import subprocess

UV_RUN_RUFF_BASE = ["uv", "run", "ruff"]

COMMANDS = {
    # `--extend-select`, not `--select`: `--select` replaces the configured rule
    # set, which drops F401 and makes RUF100 strip `# noqa: F401` comments as
    # unused. The next command then deletes the now-bare import.
    "Ruff sort and fix import and __all__": [
        *UV_RUN_RUFF_BASE,
        "check",
        ".",
        "--extend-select",
        "RUF",
        "--fix",
        "--unsafe-fixes",
    ],
    "Ruff check and fix all": [*UV_RUN_RUFF_BASE, "check", "--fix", "--unsafe-fixes"],
    "Ruff format": [*UV_RUN_RUFF_BASE, "format", "."],
    "Pyright": ["uv", "run", "pyright"],
}


def run_command(commands: list[str], /) -> None:
    print(f"\n> {' '.join(commands)}")
    subprocess.run(commands, check=True)


def main() -> int:
    for description, commands in COMMANDS.items():
        print(f"Running {description!r}")
        try:
            run_command(commands)
        except subprocess.CalledProcessError:
            print("^^^^^^^^^^^^^^^^")
            return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
