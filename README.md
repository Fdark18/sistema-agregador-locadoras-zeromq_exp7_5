# Sistema de Aluguel de Carros Esportivos - ZeroMQ

Sistema distribuido de agregacao de locadoras de carros esportivos usando padroes de mensageria ZeroMQ (PUB-SUB e REQ-REP).

## O que e o projeto

Sistema que permite consultar disponibilidade de carros esportivos em multiplas locadoras atraves de um agregador centralizado. Utiliza ZeroMQ para comunicacao assincrona entre servicos, implementando os padroes Publisher-Subscriber para broadcast de comandos e Request-Reply para coleta de respostas.

## Para que serve

- **Agregacao de dados**: Consolida informacoes de disponibilidade de carros de multiplas locadoras em tempo real
- **Comparacao de precos**: Identifica automaticamente a melhor oferta entre as locadoras disponiveis
- **Arquitetura distribuida**: Demonstra comunicacao entre servicos usando mensageria assincrona com ZeroMQ

## Como rodar o projeto

### 1. Instalar dependencias

```bash
poetry install --no-root
```

### 2. Executar o agregador (Terminal 1)

```bash
poetry run python aggregator.py
```

### 3. Executar as locadoras (Terminais 2 e 3)

**Terminal 2:**
```bash
poetry run python rental_service.py
```

**Terminal 3:**
```bash
poetry run python rental_service2.py
```

O agregador enviara automaticamente o comando `QTY` para todas as locadoras conectadas e exibira um resumo consolidado com os carros disponiveis e a melhor oferta.

## 3 Casos de Uso 

### 1. Consulta de Disponibilidade em Tempo Real
Cliente quer saber quais carros esportivos estao disponiveis para aluguel no momento. O agregador consulta todas as locadoras registradas e retorna uma lista consolidada em segundos.

### 2. Comparacao Automatica de Precos
Sistema identifica automaticamente o carro mais barato disponivel entre todas as locadoras, facilitando a tomada de decisao do cliente sem precisar consultar cada locadora individualmente.

### 3. Monitoramento de Frota Distribuida
Empresa de turismo de luxo monitora disponibilidade de carros esportivos em diferentes localizacoes (aeroporto, centro) para oferecer ao cliente a opcao mais conveniente baseada em localizacao e preco.

## Arquitetura

```
+-----------------+
|   Aggregator    |
|   PUB + REP     |
+--------+--------+
         | PUB: "QTY"
         +------------------+
         |                  |
    +----v----+        +----v----+
    | Rental  |        | Rental  |
    |Service 1|        |Service 2|
    | SUB+REQ |        | SUB+REQ |
    +---------+        +---------+
         |                  |
         +------ REQ -------+
              (envia dados)
```

## Padroes ZeroMQ Utilizados

- **PUB-SUB**: Agregador envia comandos broadcast para todas as locadoras
- **REQ-REP**: Locadoras enviam respostas individuais ao agregador
- **Multipart Messages**: Dados estruturados com PyObj para envio de objetos Python
