import logging
from typing import List, Dict, Any
from src.domain.entities import Order, OrderItem
from src.interfaces.ports import OrderRepositoryInterface, MessageBrokerInterface

logger = logging.getLogger(__name__)

class CreateOrderUseCase:
    """
    Caso de Uso: Criar Pedido (Create Order)
    Responsável por orquestrar a regra de negócio de criação, persistência e notificação.
    """

    def __init__(
        self, 
        repository: OrderRepositoryInterface, 
        broker: MessageBrokerInterface
    ):
        self.repository = repository
        self.broker = broker

    async def execute(self, customer_id: str, items_data: List[Dict[str, Any]]) -> Order:
        """
        Executa a criação do pedido.
        
        Fluxo:
        1. Converte dados brutos (dict) para Entidades de Domínio.
        2. Persiste o pedido no banco de dados.
        3. Tenta notificar outros serviços via Broker (RabbitMQ).
        
        Args:
            customer_id: ID do cliente.
            items_data: Lista de dicionários contendo 'product_id', 'quantity', 'price'.
            
        Returns:
            Order: A entidade de pedido persistida.
        """

        items = [
            OrderItem(
                product_id=item['product_id'], 
                quantity=item['quantity'], 
                price=item['price']
            ) for item in items_data
        ]
        
        order = Order(customer_id=customer_id, items=items)
        

        saved_order = await self.repository.save(order)
        logger.info(f"✅ Pedido criado com sucesso. ID: {saved_order.order_id}")


        event_payload = {
            "event": "OrderCreated",
            "data": {
                "order_id": str(saved_order.order_id),
                "customer_id": saved_order.customer_id,
                "items": [
                    {"product_id": i.product_id, "qty": i.quantity} 
                    for i in saved_order.items
                ],
                "total_amount": saved_order.total_amount,
                "timestamp": saved_order.created_at.isoformat()
            }
        }


        try:
            await self.broker.publish("stock_updates", event_payload)
            logger.info(f"📨 Evento 'OrderCreated' publicado para o pedido {saved_order.order_id}")
        except Exception as e:
            logger.error(f"⚠️ FALHA CRÍTICA DE INTEGRAÇÃO: Não foi possível enviar evento ao RabbitMQ. Erro: {e}")
            
        return saved_order