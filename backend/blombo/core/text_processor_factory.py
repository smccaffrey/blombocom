from typing import Dict, Type

from blombo.core.text_processor import TextProcessor
from blombo.core.text_processor_config import TextProcessorConfig

class TextProcessorFactory:
    """A factory class for creating text processors."""

    _processors: Dict[str, Type[TextProcessor]] = {}

    @classmethod
    def register(cls, name: str, processor_class: Type[TextProcessor]) -> None:
        """Register a text processor class with the factory.

        Args:
            name: The name of the processor.
            processor_class: The class of the processor.
        """
        cls._processors[name] = processor_class

    @classmethod
    def create(cls, name: str, config: TextProcessorConfig) -> TextProcessor:
        """Create a text processor with the given name and configuration.

        Args:
            name: The name of the processor to create.
            config: The configuration for the processor.

        Returns:
            A text processor instance.

        Raises:
            ValueError: If the processor name is not registered.
        """
        if name not in cls._processors:
            raise ValueError(f"Unknown processor: {name}")
        return cls._processors[name](config) 