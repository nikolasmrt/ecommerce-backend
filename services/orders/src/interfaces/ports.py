from abc import ABC, abstractmethod
from src.domain.entities import Order

class OrderRepositoryInterface(ABC):
    """
    Porta de Saída (Output Port) para persistência de pedidos.
    Define QUAIS métodos o banco de dados deve ter, mas não COMO implementar.
    """
    @abstractmethod
    async def save(self, order: Order) -> Order:
        pass

    @abstractmethod
    async def get_by_id(self, order_id: str) -> Order | None:
        pass

class MessageBrokerInterface(ABC):
    """
    Porta de Saída para mensageria.
    """
    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def close(self):
        pass

    @abstractmethod
    async def publish(self, queue: str, message: dict) -> None:
        pass