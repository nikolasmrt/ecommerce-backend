from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from uuid import UUID, uuid4

@dataclass
class OrderItem:
    """
    Value Object representando um item dentro do pedido.
    """
    product_id: str
    quantity: int
    price: float

    @property
    def subtotal(self) -> float:
        """Calcula o preço total deste item (qtd * preço)."""
        return self.quantity * self.price

@dataclass
class Order:
    """
    Entity (Aggregate Root) representando o Pedido.
    Contém a lógica central de dados e validações do negócio.
    """
    customer_id: str
    items: List[OrderItem]
    order_id: UUID = field(default_factory=uuid4)
    status: str = "PENDING"
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def total_amount(self) -> float:
        """
        Regra de Negócio: O total do pedido é a soma dos subtotais dos itens.
        """
        return sum(item.subtotal for item in self.items)