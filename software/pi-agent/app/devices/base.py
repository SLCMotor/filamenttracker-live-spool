from abc import ABC, abstractmethod


class ScaleDevice(ABC):
    """Base interface for all scale implementations."""

    @abstractmethod
    def is_connected(self) -> bool:
        pass

    @abstractmethod
    def is_stable(self) -> bool:
        pass

    @abstractmethod
    def get_raw_weight_grams(self) -> float:
        pass

    @abstractmethod
    def set_mock_raw_weight_grams(self, weight_grams: float) -> None:
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
