"""
Serviço de Locadora de Carros - Locadora B
Usa padrão PUB-SUB para receber comandos e REQ para enviar respostas
"""
import zmq
from datetime import datetime
from typing import List, Dict, Optional

class RentalService:
    def __init__(self, service_name: str, api_url: str, aggregator_pub_port: int = 5555, aggregator_rep_port: int = 5556):
        self.service_name = service_name
        self.api_url = api_url
        self.aggregator_pub_port = aggregator_pub_port
        self.aggregator_rep_port = aggregator_rep_port

        # Lista de carros esportivos: Id, Nome, Valor, Alugado, Tempo
        self.cars: List[Dict] = [
            {
                "id": 1,
                "nome": "2024/Aston Martin/DB11",
                "valor": 3800.00,
                "alugado": None,
                "tempo": 0
            },
            {
                "id": 2,
                "nome": "2023/Corvette/C8 Stingray",
                "valor": 2500.00,
                "alugado": datetime.now(),
                "tempo": 5
            },
            {
                "id": 3,
                "nome": "2022/Nissan/GT-R",
                "valor": 2200.00,
                "alugado": None,
                "tempo": 0
            },
            {
                "id": 4,
                "nome": "2023/Audi/R8 V10",
                "valor": 3300.00,
                "alugado": None,
                "tempo": 0
            },
            {
                "id": 5,
                "nome": "2024/BMW/M4 Competition",
                "valor": 1800.00,
                "alugado": None,
                "tempo": 0
            }
        ]

        # Contexto ZeroMQ
        self.context = zmq.Context()

        # Socket SUB para receber comandos do agregador
        self.sub_socket = self.context.socket(zmq.SUB)
        self.sub_socket.connect(f"tcp://localhost:{self.aggregator_pub_port}")
        self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, "")  # Subscreve a todos os tópicos

        # Socket REQ para enviar respostas ao agregador
        self.req_socket = self.context.socket(zmq.REQ)
        self.req_socket.connect(f"tcp://localhost:{self.aggregator_rep_port}")

        print(f"[{self.service_name}] Serviço iniciado")
        print(f"[{self.service_name}] Conectado ao agregador PUB: tcp://localhost:{self.aggregator_pub_port}")
        print(f"[{self.service_name}] Conectado ao agregador REP: tcp://localhost:{self.aggregator_rep_port}")

    def get_available_cars(self) -> List[Dict]:
        """Retorna lista de carros disponíveis (não alugados)"""
        return [
            {"nome": car["nome"], "valor": car["valor"]}
            for car in self.cars if car["alugado"] is None
        ]

    def get_available_count(self) -> int:
        """Retorna quantidade de carros disponíveis"""
        return sum(1 for car in self.cars if car["alugado"] is None)

    def handle_qty_command(self):
        """Handle comando QTY - envia informações de carros disponíveis"""
        available_count = self.get_available_count()
        available_cars = self.get_available_cars()

        print(f"\n[{self.service_name}] Processando comando QTY")
        print(f"[{self.service_name}] Carros disponíveis: {available_count}")
        print(f"[{self.service_name}] Lista: {available_cars}")

        # Envia resposta multipart: [API URL, quantidade, lista de carros]
        response_data = {
            "service_name": self.service_name,
            "api_url": self.api_url,
            "count": available_count,
            "cars": available_cars
        }

        self.req_socket.send_pyobj(response_data)
        print(f"[{self.service_name}] Resposta enviada ao agregador")

        # Aguarda ACK
        ack = self.req_socket.recv_string()
        print(f"[{self.service_name}] Recebido: {ack}")

    def run(self):
        """Execução principal do serviço"""
        print(f"\n[{self.service_name}] Aguardando comandos do agregador...")

        try:
            # Aguarda comando
            message = self.sub_socket.recv_string()
            print(f"[{self.service_name}] Comando recebido: {message}")

            if message == "QTY":
                self.handle_qty_command()
            else:
                print(f"[{self.service_name}] Comando desconhecido: {message}")

        except KeyboardInterrupt:
            print(f"\n[{self.service_name}] Encerrando serviço...")
        finally:
            self.cleanup()

    def cleanup(self):
        """Limpa recursos"""
        self.sub_socket.close()
        self.req_socket.close()
        self.context.term()
        print(f"[{self.service_name}] Serviço encerrado")


if __name__ == "__main__":
    service = RentalService(
        service_name="Locadora B - Aeroporto",
        api_url="http://api.locadora-b.com.br/rental"
    )
    service.run()
