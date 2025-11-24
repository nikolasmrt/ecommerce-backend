import sys
import os
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Configuração de Path (Bootstrap) 
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Imports da Aplicação
from src.infrastructure.messaging import RabbitMQPublisher, LogBroker
from src.infrastructure.repositories import InMemoryOrderRepository
from src.application.use_cases import CreateOrderUseCase
from src.domain.entities import Order

# Configurações de Ambiente
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

USE_MOCK_BROKER = True 

# Injeção de Dependências
repository = InMemoryOrderRepository()

if USE_MOCK_BROKER:
    broker = LogBroker()
else:
    broker = RabbitMQPublisher(RABBITMQ_URL)

create_order_use_case = CreateOrderUseCase(repository, broker)

# Ciclo de Vida da Aplicação
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia a conexão com serviços externos ao iniciar/desligar a API."""
    try:
        await broker.connect()
    except Exception as e:
        print(f"⚠️ Aviso: Falha ao conectar no Broker: {e}")
    
    yield
    
    await broker.close()

# Definição da API
app = FastAPI(
    title="Order Service",
    description="API de microsserviço para gestão de pedidos.",
    version="1.0.0",
    lifespan=lifespan
)

# DTOs
class OrderItemDTO(BaseModel):
    product_id: str
    quantity: int = Field(..., gt=0, description="Quantidade deve ser maior que zero")
    price: float = Field(..., gt=0, description="Preço unitário")

class CreateOrderRequest(BaseModel):
    customer_id: str
    items: List[OrderItemDTO]

# Rotas
@app.post("/orders", status_code=201, summary="Criar novo pedido")
async def create_order_endpoint(payload: CreateOrderRequest):
    """
    Recebe um pedido, persiste no banco e notifica o serviço de estoque.
    """
    try:
        
        items_dict = [item.model_dump() for item in payload.items]
        
        
        order = await create_order_use_case.execute(
            customer_id=payload.customer_id,
            items_data=items_dict
        )
        
        
        return {
            "order_id": str(order.order_id),
            "status": order.status,
            "total_amount": order.total_amount,
            "message": "Order created successfully."
        }
    except Exception as e:
        
        print(f"❌ Erro crítico ao criar pedido: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")