"""
Serviço Agregador de Aluguel de Carros
Usa padrão PUB para enviar comandos e REP para receber respostas das locadoras
"""
import zmq
import zmq.utils.win32
import time
from typing import List, Dict

class Main():
    # URLs para conexões
    _pub_ch = "tcp://*:5555"  # Socket PUB para enviar comandos
    _rep_ch = "tcp://*:5556"  # Socket REP para receber respostas

    def __init__(self, context=None):
        self.c = context or zmq.Context.instance()  # Contexts are threadsafe, singleton

        # Socket PUB para enviar comandos às locadoras
        self.pub_socket = self.c.socket(zmq.PUB)

        # Socket REP para receber respostas das locadoras
        self.rep_socket = self.c.socket(zmq.REP)

        print("=" * 60)
        print("AGREGADOR DE LOCADORAS DE CARROS")
        print("=" * 60)

    def request_availability(self, num_responses: int = 2):
        """
        Envia comando QTY para todas as locadoras e aguarda respostas

        Args:
            num_responses: Número esperado de respostas das locadoras
        """
        print("\n" + "=" * 60)
        print("CONSULTANDO DISPONIBILIDADE DE CARROS")
        print("=" * 60)

        # Envia comando QTY via PUB
        print("\n[AGREGADOR] Enviando comando QTY para todas as locadoras...")
        self.pub_socket.send_string("QTY")
        print("[AGREGADOR] Comando enviado via PUB")

        # Aguarda respostas das locadoras via REP
        print(f"\n[AGREGADOR] Aguardando {num_responses} resposta(s)...\n")

        all_rentals: List[Dict] = []

        for i in range(num_responses):
            try:
                # Configura timeout de 5 segundos
                self.rep_socket.setsockopt(zmq.RCVTIMEO, 5000)

                # Recebe resposta da locadora
                rental_data = self.rep_socket.recv_pyobj()

                print(f"\n--- Resposta {i+1} ---")
                print(f"Locadora: {rental_data['service_name']}")
                print(f"API URL: {rental_data['api_url']}")
                print(f"Carros disponíveis: {rental_data['count']}")
                print(f"Lista de carros:")
                for car in rental_data['cars']:
                    print(f"  - {car['nome']}: R$ {car['valor']:.2f}/dia")

                all_rentals.append(rental_data)

                # Envia ACK
                self.rep_socket.send_string("ACK")
                print(f"[AGREGADOR] ACK enviado para {rental_data['service_name']}")

            except zmq.Again:
                print(f"\n[AGREGADOR] Timeout aguardando resposta {i+1}")
                break
            except Exception as e:
                print(f"\n[AGREGADOR] Erro ao receber resposta {i+1}: {e}")
                break

        # Exibe resumo consolidado
        self.display_summary(all_rentals)

    def display_summary(self, rentals: List[Dict]):
        """Exibe resumo consolidado de todas as locadoras"""
        print("\n" + "=" * 60)
        print("RESUMO CONSOLIDADO")
        print("=" * 60)

        total_cars = sum(rental['count'] for rental in rentals)
        total_rentals = len(rentals)

        print(f"\nTotal de locadoras respondidas: {total_rentals}")
        print(f"Total de carros disponíveis: {total_cars}")

        if total_cars > 0:
            print("\n--- Carros disponíveis por locadora ---")
            for rental in rentals:
                print(f"\n{rental['service_name']} ({rental['count']} carros):")
                for car in rental['cars']:
                    print(f"  {car['nome']} - R$ {car['valor']:.2f}/dia")

            # Encontra o carro mais barato
            all_cars = []
            for rental in rentals:
                for car in rental['cars']:
                    all_cars.append({
                        'locadora': rental['service_name'],
                        'nome': car['nome'],
                        'valor': car['valor']
                    })

            cheapest = min(all_cars, key=lambda x: x['valor'])
            print(f"\n--- Melhor oferta ---")
            print(f"{cheapest['nome']} - R$ {cheapest['valor']:.2f}/dia")
            print(f"Locadora: {cheapest['locadora']}")

        print("\n" + "=" * 60)

    def run(self):
        with self.pub_socket as pub_s, self.rep_socket as rep_s:
            # Bind dos sockets
            pub_s.bind(Main._pub_ch)
            rep_s.bind(Main._rep_ch)

            print(f"Socket PUB iniciado: {Main._pub_ch}")
            print(f"Socket REP iniciado: {Main._rep_ch}")
            print("=" * 60)

            # Aguarda um tempo para as locadoras se conectarem
            print("\nAguardando conexões das locadoras...")
            time.sleep(2)

            # Solicita disponibilidade (esperando 2 locadoras)
            self.request_availability(num_responses=2)

def w32hk():
    zmq.Context.instance().term()

if __name__ == '__main__':
    try:
        with zmq.utils.win32.allow_interrupt(w32hk):
            Main().run()
    except KeyboardInterrupt:
        print("\n[AGREGADOR] End.")
