from abc import ABC, abstractmethod


class Changeable(ABC):
    @abstractmethod
    def changed(self):
        raise NotImplementedError()