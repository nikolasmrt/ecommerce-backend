import aio_pika
import json
import logging
from src.interfaces.ports import MessageBrokerInterface

logger = logging.getLogger(__name__)

class RabbitMQPublisher(MessageBrokerInterface):
    """Implementação real do Broker usando RabbitMQ."""
    def __init__(self, amqp_url: str):
        self.amqp_url = amqp_url
        self.connection = None
        self.channel = None

    async def connect(self):
        logger.info(f"Conectando ao RabbitMQ em: {self.amqp_url}")
        self.connection = await aio_pika.connect_robust(self.amqp_url)
        self.channel = await self.connection.channel()
        await self.channel.declare_queue("stock_updates", durable=True)

    async def close(self):
        if self.connection:
            await self.connection.close()

    async def publish(self, queue: str, message: dict) -> None:
        if not self.channel:
            raise ConnectionError("RabbitMQ channel is not initialized")
        
        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(message).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key=queue
        )

class LogBroker(MessageBrokerInterface):
    """
    Broker 'Mock' (Simulado) para desenvolvimento local sem Docker.
    Apenas loga as mensagens no console (stdout).
    """
    async def connect(self):
        print("\n🟢 [MOCK] Conectado ao sistema de mensagens simulado.")

    async def close(self):
        print("🔴 [MOCK] Conexão simulada fechada.")

    async def publish(self, queue: str, message: dict) -> None:
        print(f"\n📨 [MOCK] Enviando evento para fila '{queue}':")
        print(f"   Conteúdo: {message}")