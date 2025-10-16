"""
Serviço de Locadora de Carros - Locadora A
Usa padrão PUB-SUB para receber comandos e REQ para enviar respostas
"""
import zmq
import zmq.utils.win32
from datetime import datetime
from typing import List, Dict, Optional

class Main():
    # URLs para conexões
    _sub_ch = "tcp://localhost:5555"  # Socket SUB para receber comandos
    _req_ch = "tcp://localhost:5556"  # Socket REQ para enviar respostas

    def __init__(self, context: Optional[zmq.Context] = None):
        self.c = context or zmq.Context.instance()  # Contexts are threadsafe, singleton

        # Dados do serviço
        self.service_name = "Locadora A - Centro"
        self.api_url = "http://api.locadora-a.com.br/rental"

        # Lista de carros esportivos: Id, Nome, Valor, Alugado, Tempo
        self.cars: List[Dict[str, any]] = [
            {
                "id": 1,
                "nome": "2023/Ferrari/F8 Tributo",
                "valor": 3500.00,
                "alugado": None,
                "tempo": 0
            },
            {
                "id": 2,
                "nome": "2024/McLaren/720S",
                "valor": 3200.00,
                "alugado": None,
                "tempo": 0
            },
            {
                "id": 3,
                "nome": "2022/Lamborghini/Huracan",
                "valor": 4000.00,
                "alugado": datetime.now(),
                "tempo": 3
            },
            {
                "id": 4,
                "nome": "2023/Porsche/911 Turbo S",
                "valor": 2800.00,
                "alugado": None,
                "tempo": 0
            }
        ]

        # Socket SUB para receber comandos do agregador
        self.sub_socket = self.c.socket(zmq.SUB)

        # Socket REQ para enviar respostas ao agregador
        self.req_socket = self.c.socket(zmq.REQ)

    def get_available_cars(self) -> List[Dict[str, any]]:
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
        with self.sub_socket as sub_s, self.req_socket as req_s:
            # Connect dos sockets
            sub_s.connect(Main._sub_ch)
            sub_s.setsockopt_string(zmq.SUBSCRIBE, "")  # Subscreve a todos os tópicos

            req_s.connect(Main._req_ch)

            print(f"[{self.service_name}] Serviço iniciado")
            print(f"[{self.service_name}] Conectado ao agregador PUB: {Main._sub_ch}")
            print(f"[{self.service_name}] Conectado ao agregador REP: {Main._req_ch}")

            print(f"\n[{self.service_name}] Aguardando comandos do agregador...")

            # Aguarda comando
            message = sub_s.recv_string()
            print(f"[{self.service_name}] Comando recebido: {message}")

            if message == "QTY":
                self.handle_qty_command()
            else:
                print(f"[{self.service_name}] Comando desconhecido: {message}")

def w32hk():
    zmq.Context.instance().term()

if __name__ == '__main__':
    try:
        with zmq.utils.win32.allow_interrupt(w32hk):
            Main().run()
    except KeyboardInterrupt:
        print(f"\n[Locadora A] End.")
