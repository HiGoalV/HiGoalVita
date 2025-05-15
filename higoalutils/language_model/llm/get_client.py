# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""Initialize LLM and Embedding clients."""
import logging

from higoalutils.config.models.embedding_config import EmbeddingConfig
from higoalutils.config.enums.sys_enums import EmbeddingType
from higoalutils.language_model.llm.base import BaseTextEmbedding
from higoalutils.language_model.llm.huggingface_embedding.embedding import HuggingFaceEmbedding
from higoalutils.language_model.llm.oai.chat_openai import ChatOpenAI
from higoalutils.language_model.llm.oai.embedding import OpenAIEmbedding
from higoalutils.language_model.llm.oai.typing import OpenaiApiType
from higoalutils.config.models.langeuage_model_config import LanguageModelConfig
from higoalutils.config.load_model_info import get_model_info


log = logging.getLogger(__name__)

def get_llm(
    config: LanguageModelConfig, 
    model_name: str | None = None, 
    isJson: bool = False
) -> ChatOpenAI:
    """Get the LLM client."""
    default_llm_settings = config
    model_name = model_name or default_llm_settings.default_model
    llm_model = get_model_info().get_by_model_name(model_name)
    debug_llm_key = llm_model.api_key or "" # type: ignore
    llm_debug_info = {
        **default_llm_settings.model_dump(),
        "api_key": f"REDACTED,len={len(debug_llm_key)}",
    }
    log.info(f"creating llm client with {llm_debug_info}")  # noqa T201
    return ChatOpenAI(
        api_key=llm_model.api_key, # type: ignore
        api_base=llm_model.api_base, # type: ignore
        model=model_name,
        encoding_model=default_llm_settings.default_encoding_model,
        api_type=OpenaiApiType.OpenAI,
        max_retries=default_llm_settings.max_retries,
        request_timeout=default_llm_settings.request_timeout,
    )


def get_text_embedder(config: EmbeddingConfig) -> BaseTextEmbedding:
    """Get the LLM client for embeddings."""
    embeddings_llm_settings = config
    model_info = get_model_info()
    model_type = embeddings_llm_settings.embedding_model_config.type
    
    if model_type == EmbeddingType.OpenAI:
        oai_cfg = embeddings_llm_settings.openai_embedding_config
        oai_model = model_info.get_by_model_name(oai_cfg.default_model) # type: ignore
        debug_embedding_api_key = oai_model.api_key or "" # type: ignore
        llm_debug_info = {
            **embeddings_llm_settings.model_dump(),
            "api_key": f"REDACTED,len={len(debug_embedding_api_key)}",
        }
        log.info(f"creating embedding llm client with {llm_debug_info}")  # noqa T201
        return OpenAIEmbedding(
            api_key=oai_model.api_key, # type: ignore
            api_base=oai_model.api_base, # type: ignore
            api_type=OpenaiApiType.OpenAI,
            model=oai_model.model_name, # type: ignore
            max_retries=oai_cfg.max_retries, # type: ignore
        )
    
    elif model_type == EmbeddingType.HuggingFace:
        hg_cfg = embeddings_llm_settings.huggingface_embedding_config
        hg_model = model_info.get_by_model_name(hg_cfg.default_model) # type: ignore
        return HuggingFaceEmbedding(
            model=hg_model.model_name,  # type: ignore
            device=hg_cfg.device,  # type: ignore
        )

    else:
        raise ValueError(
            f"Unsupported embedding model type: {embeddings_llm_settings.embedding_model_config.type}"
        )
