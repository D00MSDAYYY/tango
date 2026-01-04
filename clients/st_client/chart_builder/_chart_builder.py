from abc import ABC, abstractmethod


class _chart_builder(ABC):
    def __init__(self):
        super().__init__()

    # TODO to be honest, this 2 methods must be replaced with 3 classes - Configurator and Builder and Factory (for producing ) but later
    @abstractmethod
    def get_new_chart_settings(self) -> dict | None:
        pass

    @abstractmethod
    def build_chart_from_settings(self, chart_settings) -> _bc._base_chart | None:
        pass
