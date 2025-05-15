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

from typing import Iterator
from itertools import islice
from higoalutils.language_model.tokenizer.get_tokenizer import get_tokenizer

def batched(iterable: Iterator, n: int):
    """Batch data into tuples of length n."""
    if n < 1:
        raise ValueError("n must be at least one")
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch

def chunk_text(
    text: str,
    max_tokens: int,
    tokenizer_name: str = "cl100k_base"
) -> Iterator[str]:
    """
    Chunk text by token length using a tokenizer from the tokenizer factory.
    """
    tokenizer = get_tokenizer(tokenizer_name)
    tokens = tokenizer.encode(text)
    for chunk in batched(iter(tokens), max_tokens):
        yield tokenizer.decode(list(chunk))

def num_tokens(text: str, tokenizer_name: str = "cl100k_base") -> int:
    """
    Count the number of tokens in text using the given tokenizer.
    """
    tokenizer = get_tokenizer(tokenizer_name)
    return tokenizer.count_tokens(text)