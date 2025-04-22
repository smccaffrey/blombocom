from typing import Any, List, Optional

import openai
from openai import OpenAI

from blombo.core.text_processor import TextProcessor
from blombo.core.text_processor_config import TextProcessorConfig

class OpenAITextProcessor(TextProcessor):
    """OpenAI implementation of the text processor."""

    def __init__(self, config: TextProcessorConfig):
        """Initialize the OpenAI text processor.

        Args:
            config: Configuration for the text processor.
        """
        super().__init__(config)
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.api_base,
            api_version=config.api_version,
        )

    def process(self, text: str, **kwargs: Any) -> str:
        """Process the input text using OpenAI's API.

        Args:
            text: The input text to process.
            **kwargs: Additional arguments for processing.

        Returns:
            The processed text.
        """
        response = self.client.chat.completions.create(
            model=self.config.model_name,
            messages=[{"role": "user", "content": text}],
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            top_p=self.config.top_p,
            frequency_penalty=self.config.frequency_penalty,
            presence_penalty=self.config.presence_penalty,
            stop=self.config.stop,
            **kwargs
        )
        return response.choices[0].message.content

    def batch_process(self, texts: List[str], **kwargs: Any) -> List[str]:
        """Process a batch of texts using OpenAI's API.

        Args:
            texts: List of input texts to process.
            **kwargs: Additional arguments for processing.

        Returns:
            List of processed texts.
        """
        return [self.process(text, **kwargs) for text in texts]

    def get_embeddings(self, text: str) -> List[float]:
        """Get embeddings for the input text using OpenAI's API.

        Args:
            text: The input text to get embeddings for.

        Returns:
            List of embedding values.
        """
        response = self.client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding

    def get_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for a batch of texts using OpenAI's API.

        Args:
            texts: List of input texts to get embeddings for.

        Returns:
            List of embedding lists.
        """
        response = self.client.embeddings.create(
            model="text-embedding-ada-002",
            input=texts
        )
        return [data.embedding for data in response.data] 