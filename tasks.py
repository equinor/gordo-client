"""Management tasks."""
import sys
from typing import List

from invoke import Exit, Failure, Result, UnexpectedExit, task

SAFETY_IGNORE = ()


class _CollectFailures:
    def __init__(self, ctx):
        self._failed: List[Result] = []
        self._ctx = ctx

    def run(self, command: str, **kwargs):
        kwargs.setdefault("warn", True)
        cmd_result: Result = self._ctx.run(command, **kwargs)
        if cmd_result.ok:
            self._ctx.run("echo Ok")
        else:
            self._failed.append(cmd_result)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._failed:
            raise UnexpectedExit(self._failed[0])


def _get_changed_files(ctx, extension=".py"):
    output = ctx.run("git diff --name-only", hide=True).stdout
    return " ".join(f for f in output.splitlines() if extension and f.endswith(extension))


@task
def test(ctx):
    """Run tests."""
    # Note: use commandline arguments instead of using `adopts` in `setup.cfg`,
    # since pytest-cov breaks Intellij IDEA debugger.
    ctx.run("poetry run pytest --cov=gordo.client -vv .", pty=True)


@task
def check(ctx):
    """Run all static checks."""
    ok = True
    for check_task in (check_code, check_safety):
        try:
            check_task(ctx)
        except Failure:
            ok = False

    if ok:
        print("All checks passed.")
    else:
        raise Exit("One or more checks failed.")


@task(help={"diff": "Check only the changed files."})
def check_code(ctx, diff=False):
    """Run static checks on Python code."""
    files_to_check = _get_changed_files(ctx) if diff else ""
    if diff and not files_to_check:
        print("No changed files, skipping.")
        return

    with _CollectFailures(ctx) as new_ctx:
        print("Checking Black formatting.")
        new_ctx.run(f"poetry run black  --check -- { files_to_check or '.' }")

        print("Checking the style.")
        new_ctx.run(f"poetry run flake8 -- { files_to_check }")

        print("Checking type safety.")
        new_ctx.run(f"poetry run mypy { files_to_check or '.' }")


@task
def check_safety(ctx):
    """Check third-party dependencies for known security vulnerabilities."""
    print("Checking the libraries.")
    ignores = " ".join(f"--ignore { n }" for n in SAFETY_IGNORE)
    if SAFETY_IGNORE:
        print("WARNING: Ignored issues:", ", ".join(SAFETY_IGNORE), file=sys.stderr)
    ctx.run(f"poetry run safety check --full-report { ignores }")


@task(help={"diff": "Check only the changed files."})
def fmt(ctx, diff=False):
    """Apply automatic code formatting."""
    files_to_check = _get_changed_files(ctx) if diff else "."
    if not files_to_check:
        print("No changed files, skipping.")
        return

    with _CollectFailures(ctx) as new_ctx:
        new_ctx.run(f"poetry run isort -rc { files_to_check }")
        new_ctx.run(f"poetry run black { files_to_check }")
