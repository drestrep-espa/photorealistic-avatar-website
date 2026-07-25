from abc import ABC, abstractmethod


class ReportGenerator(ABC):
    @abstractmethod
    def generate(self, content: str, output_dir: str) -> str:
        raise NotImplementedError  # pragma: no cover
