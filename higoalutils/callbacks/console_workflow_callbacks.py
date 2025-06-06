# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""A logger that emits updates from the indexing engine to the console."""

from higoalutils.callbacks.noop_workflow_callbacks import NoopWorkflowCallbacks


class ConsoleWorkflowCallbacks(NoopWorkflowCallbacks):
    """A logger that writes to a console."""

    def error(
        self,
        message: str,
        cause: BaseException | None = None,
        stack: str | None = None,
        details: dict | None = None,
    ):
        """Handle when an error occurs."""
        print(message, str(cause), stack, details)  # noqa T201

    def warning(self, message: str, details: dict | None = None):
        """Handle when a warning occurs."""
        _print_warning(message)

    def log(self, message: str, details: dict | None = None):
        """Handle when a log message is produced."""
        print(message, details)  # noqa T201


def _print_warning(skk):
    print("\033[93m {}\033[00m".format(skk))  # noqa T201
