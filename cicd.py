import os
import subprocess
from typing import Any, List

from halo import Halo


def run_bash_and_check(command: List[str], stdout: Any = None, stderr: Any = None) -> None:
    if stdout or stderr:
        subprocess.run(command, check=True, stdout=stdout, stderr=stderr)
    else:
        subprocess.run(command, check=True)


def fmt() -> None:
    """Format code."""
    spinner = Halo(text="> Running yapf on project", spinner="arc", placement="right")
    spinner.start()
    run_bash_and_check(["python3", "-m", "yapf", "--recursive", "-i", "bra_database"])
    run_bash_and_check(["python3", "-m", "isort", "bra_database"])
    spinner.succeed()


def flake() -> None:
    """Check lint."""
    spinner = Halo(text="> Running Flake8 on project", spinner="arc", placement="right")
    spinner.start()
    run_bash_and_check(["python3", "-m", "flake8", "bra_database"])
    spinner.succeed()


def lint() -> None:
    """Check lint."""
    spinner = Halo(text="> Running PyLint on project", spinner="arc", placement="right")
    spinner.start()
    run_bash_and_check(["python3", "-m", "pylint", "bra_database"])
    spinner.succeed()


def bandit() -> None:
    """Check security issues."""
    spinner = Halo(text="> Running FLake8-bandit on project", spinner="arc", placement="right")
    spinner.start()
    run_bash_and_check(["python3", "-m", "bandit", "--exit-zero", "-r", "bra_database"])
    spinner.succeed()


def coverage() -> None:
    """Perform coverage analysis."""
    spinner = Halo(text="> Checking code coverage", spinner="dots", placement="left")
    spinner.start()
    run_bash_and_check(["python3", "-m", "coverage",  "run", "-m", "pytest", "tests"])
    run_bash_and_check(["python3", "-m", "coverage",  "report", "-m"])
    spinner.succeed()


def unit_tests() -> None:
    """Perform tests."""
    spinner = Halo(text="> Running project's unit tests", spinner="dots", placement="left")
    spinner.start()
    run_bash_and_check(["python3", "-m", "pytest",  "-q", "tests"])
    spinner.succeed()
