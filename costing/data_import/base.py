"""
Abstract Base Class for Engineering Project Importers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Union, BinaryIO
from pathlib import Path


class BaseProjectImporter(ABC):
    """
    Интерфейс импортера проектных данных (MiTek, Excel, IFC, XML).
    """

    @abstractmethod
    def parse(self, source: Union[str, Path, BinaryIO, bytes]) -> Dict[str, Any]:
        """
        Парсинг источника данных и возвращение нормализованной структуры проекта.
        """
        pass
