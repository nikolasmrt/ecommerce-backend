from typing import Dict, Optional
from src.interfaces.ports import OrderRepositoryInterface
from src.domain.entities import Order

class InMemoryOrderRepository(OrderRepositoryInterface):
    """
    Implementação em memória do repositório.
    Ideal para testes unitários e prototipagem rápida sem banco de dados real.
    """
    def __init__(self):
        
        self._storage: Dict[str, Order] = {}

    async def save(self, order: Order) -> Order:
        """
        Salva o pedido no dicionário em memória.
        Em produção, aqui entraria: session.add(order); session.commit()
        """
        self._storage[str(order.order_id)] = order
        return order

    async def get_by_id(self, order_id: str) -> Optional[Order]:
        return self._storage.get(order_id)