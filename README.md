# 🛒 E-commerce Microservices Backend

Sistema de backend distribuído para E-commerce, desenvolvido com foco em escalabilidade, desacoplamento e resiliência. O projeto utiliza **Clean Architecture**, **Python (FastAPI)** e mensageria assíncrona com **RabbitMQ**.

---

## 🏗️ Visão Geral da Arquitetura

O sistema adota uma arquitetura orientada a eventos. O Serviço de Pedidos recebe a requisição, persiste os dados e publica um evento de domínio, liberando o cliente imediatamente enquanto processos secundários (baixa de estoque, envio de e-mail) ocorrem em background.

### Diagrama de Fluxo

```mermaid
graph LR
    Client[Cliente / Frontend] -- POST /orders --> API[API Gateway / Controller]
    
    subgraph "Order Service (Clean Architecture)"
        API -- DTO --> UC[Use Case: CreateOrder]
        UC -- Entidade --> Repo[Repositório]
        UC -- Evento --> BrokerAdapter[RabbitMQ Adapter]
    end
    
    Repo -- SQL --> DB[(Banco de Dados)]
    BrokerAdapter -- Async Msg --> Queue[[RabbitMQ Queue]]
    Queue -.-> Inventory[Serviço de Estoque]
    
    style Client fill:#f9f,stroke:#333,stroke-width:2px
    style API fill:#bbf,stroke:#333,stroke-width:2px
    style UC fill:#bfb,stroke:#333,stroke-width:2px
    style Queue fill:#ff9,stroke:#333,stroke-width:2px


ecommerce-backend/
├── docker-compose.yml           # Orquestração da Infraestrutura
├── README.md                    # Documentação
└── services/
    └── orders/                  # Microsserviço de Pedidos
        ├── Dockerfile           # Imagem do serviço
        ├── requirements.txt     # Dependências (FastAPI, aio-pika)
        └── src/
            ├── main.py          # Entrypoint & Configuração
            ├── domain/          # Entidades & Regras de Negócio Puras
            ├── application/     # Casos de Uso (Orquestração)
            ├── interfaces/      # Portas (Contratos Abstratos)
            └── infrastructure/  # Implementações (RabbitMQ, Repositórios)
    