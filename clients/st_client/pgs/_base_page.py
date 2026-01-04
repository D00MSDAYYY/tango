from abc import ABC, abstractmethod


class _base_page(ABC):
    def __init__(self, name, settings):
        self.settings = settings
        self.name = name

    @abstractmethod
    def __call__(self):
        pass
