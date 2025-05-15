# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""创建pipeline_reporter."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Generic, Literal, TypeVar, cast

from pydantic import BaseModel, Field

from higoalutils.callbacks.console_workflow_callbacks import ConsoleWorkflowCallbacks
from higoalutils.callbacks.file_workflow_callbacks import FileWorkflowCallbacks
from higoalutils.config.enums import ReportingType
from higoalutils.config.models import ReportingConfig

if TYPE_CHECKING:
    from higoalutils.callbacks.workflow_callbacks import WorkflowCallbacks

def create_pipeline_reporter(
    config: ReportingConfig, root_dir: str | None, time_zone: str
) -> WorkflowCallbacks:
    """Create a logger for the given pipeline config."""

    match config.type:
        case ReportingType.file:
            return FileWorkflowCallbacks(report_config=config, time_zone=time_zone)
        case ReportingType.console:
            return ConsoleWorkflowCallbacks()
        case _:
            msg = f"Unknown reporting type: {config.type}"
            raise ValueError(msg)
