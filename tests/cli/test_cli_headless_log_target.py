from io import StringIO

from rich.console import Console

from cai import cli_headless


def test_print_session_log_target_ignores_none_filepath() -> None:
    buf = StringIO()
    console = Console(file=buf, width=120, force_terminal=False)

    cli_headless._print_session_log_target(console, None)

    assert buf.getvalue() == ""
