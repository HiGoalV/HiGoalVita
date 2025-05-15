# Copyright 2025 HiGoal Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""提示词构建模块。"""

import yaml

from higoalcore.config.enums.query_enums import PromptFileType, SearchMethod
from higoalcore.query.prompts.prompt_types import BasicSearch
from higoalutils.storage.file_pipeline_storage import FilePipelineStorage
from higoalutils.utils.language_utils.detect_language import detect_language


async def get_prompt_template(
    query_text: str,
    search_method: SearchMethod = SearchMethod.BASIC,
    root_dir: str = "datavolume",
    prompt_dir: str = "prompts",
    language_threshold: float = 0.3,
    prompt_file_type: PromptFileType = PromptFileType.YAML,
) -> str:
    file_path = FilePipelineStorage(f"{root_dir}/{prompt_dir}")
    prompt_file_name = ""
    if prompt_file_type == PromptFileType.YAML:
        extention = PromptFileType.YAML.value
    else:
        extention = PromptFileType.TXT.value
    match search_method:
        case search_method.BASIC:
            prompt_file_name = f"{BasicSearch.file.value}{extention}"
            key = BasicSearch.prompt.value
    
    if not await file_path.has(prompt_file_name):
        raise ValueError(f"Prompt file {file_path}/{prompt_file_name} does not exist!")
    prompt = await file_path.get(prompt_file_name)
    if not prompt:
        raise ValueError(f"Prompt file {file_path}/{prompt_file_name} is empty!")
    
    language_code = detect_language(query_text, language_threshold) 

    if prompt_file_type == PromptFileType.YAML:
        prompt_dict = yaml.safe_load(prompt)
        if not prompt_dict[key]: # type: ignore
            raise ValueError(f"Prompt file {file_path}/{prompt_file_name} prompt {key} is empty!") # type: ignore
        prompt = prompt_dict[key].replace("{language_code_var}",language_code) # type: ignore
    else:
        prompt = prompt.replace("{language_code_var}",language_code)
    return prompt

def complete_prompt(
    query: str,
    prompt: str,
    context: str,
    response_type: str | None = None
) -> list[str]:
    """构建完整的提示词"""
    messages = []
    final_prompt = prompt
    if not response_type:
        final_prompt = final_prompt.replace("{response_type}","文本以Markdown格式回答")
    else:
        final_prompt = final_prompt.replace("{response_type}",response_type)
    final_prompt = final_prompt.replace("{context_data}",context)
    final_prompt = final_prompt.replace("{question}",query)
    messages.append({"role": "user", "content": final_prompt})
    return messages  
