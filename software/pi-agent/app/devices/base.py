from abc import ABC, abstractmethod


class ScaleDevice(ABC):
    """Base interface for all scale implementations."""

    @abstractmethod
    def is_connected(self) -> bool:
        pass

    @abstractmethod
    def get_weight_grams(self) -> float | None:
        pass

    @abstractmethod
    def tare(self) -> bool:
        pass


class NfcDevice(ABC):
    """Base interface for all NFC reader implementations."""

    @abstractmethod
    def is_connected(self) -> bool:
        pass

    @abstractmethod
    def read_tag(self) -> str | None:
        pass

    @abstractmethod
    def write_tag(self, data: str) -> bool:
        pass
