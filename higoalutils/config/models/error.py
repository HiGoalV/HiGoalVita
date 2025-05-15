# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License


class ApiKeyMissingError(ValueError):
    """LLM Key missing error."""

    def __init__(self, llm_type: str) -> None:
        """Init method definition."""
        msg = f"API Key is required for {llm_type}"
        msg += ". Please set the API_KEY."
        super().__init__(msg)


class LanguageModelConfigMissingError(ValueError):
    """Missing model configuration error."""

    def __init__(self, key: str = "") -> None:
        """Init method definition."""
        msg = f'A {key} model configuration is required. Please set models["{key}"] in system_config.yaml.'
        super().__init__(msg)


class ConflictingSettingsError(ValueError):
    """Missing model configuration error."""

    def __init__(self, msg: str) -> None:
        """Init method definition."""
        super().__init__(msg)