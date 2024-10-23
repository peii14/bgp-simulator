import json
import socket
import threading
import time
import os

from utils.routing_table import RoutingTable
from trust.trust_model import TrustModel
from trust.vote_mechanism import VotingMechanism

with open('config.json') as config_file:
    config = json.load(config_file)

def get_router_config(router_id):
    """Get router configuration based on its ID."""
    for router in config['routers']:
        if router['id'] == router_id:
            return router
    return None

BGP_OPEN = "OPEN"
BGP_KEEPALIVE = "KEEPALIVE"
BGP_UPDATE = "UPDATE"
BGP_WITHDRAW = "WITHDRAW"

HOLD_TIMER = config['bgp_defaults']['hold_timer']
KEEPALIVE_INTERVAL = config['bgp_defaults']['keepalive_interval']

class BGP_Router:
    def __init__(self, router_id):
        self.config = get_router_config(router_id)
        self.router_id = self.config['id']
        self.ip = self.config['ip']
        self.neighbors = self.config['neighbors']
        self.routing_table = RoutingTable(self.router_id)
        self.trust_model = TrustModel(self.config['trust']['direct_trust'])
        self.voting_mechanism = VotingMechanism(self.router_id, self.neighbors)
        self.sockets = {}
        self.keepalive_received = {}
        self.down_routers = set() 

        self.initialize_routing_table()

        self.start_router()

    def initialize_routing_table(self):
        """Populate routing table at startup based on configuration."""
        for route in self.config['routing_table']:
            network = route['network']
            next_hop = route['next_hop']
            as_path = route['as_path']
            self.routing_table.add_route(network, next_hop, as_path)
        self.routing_table.print_routing_table()

    def start_router(self):
        """Start all router threads for communication and operations."""
        
        listener_thread = threading.Thread(target=self.listen_for_neighbors)
        listener_thread.daemon = True
        listener_thread.start()

        time.sleep(5) 
        self.connect_to_neighbors()

        keepalive_thread = threading.Thread(target=self.send_keepalive)
        keepalive_thread.daemon = True
        keepalive_thread.start()

        voting_thread = threading.Thread(target=self.exchange_votes_with_neighbors)
        voting_thread.daemon = True
        voting_thread.start()

        failure_detection_thread = threading.Thread(target=self.check_for_neighbor_failures)
        failure_detection_thread.daemon = True
        failure_detection_thread.start()

        thread_monitor = threading.Thread(target=self.check_threads)
        thread_monitor.daemon = True
        thread_monitor.start()
        print(f"All threads started for Router {self.router_id}")
    
    def check_threads(self):
        """Check if the critical threads are alive."""
        while True:
            print("Checking threads...")
            print(f"Keepalive thread is alive: {threading.current_thread().is_alive()}")
            time.sleep(60)

    def listen_for_neighbors(self):
        """Listen for connections from neighbor routers."""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.ip, 179))  
        server_socket.listen(5)
        print(f"Router {self.router_id} listening for neighbors on {self.ip}...")

        while True:
            conn, addr = server_socket.accept()
            neighbor_id = self.get_neighbor_by_ip(addr[0])
            if neighbor_id:
                print(f"Router {self.router_id} accepted connection from Router {neighbor_id}.")
                self.sockets[neighbor_id] = conn
                self.keepalive_received[neighbor_id] = time.time()
                threading.Thread(target=self.handle_neighbor_messages, args=(neighbor_id, conn), daemon=True).start()

    def connect_to_neighbors(self):
        """Connect to all neighbors."""
        for neighbor_id in self.neighbors:
            neighbor_config = get_router_config(neighbor_id)
            if neighbor_config:
                neighbor_ip = neighbor_config['ip']
                try:
                    neighbor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    neighbor_socket.connect((neighbor_ip, 179))
                    print(f"Router {self.router_id} connected to Router {neighbor_id} at {neighbor_ip}.")
                    self.sockets[neighbor_id] = neighbor_socket
                    self.keepalive_received[neighbor_id] = time.time()

                    threading.Thread(target=self.handle_neighbor_messages, args=(neighbor_id, neighbor_socket)).start()

                    # Send BGP OPEN message
                    self.send_message(neighbor_socket, BGP_OPEN)
                except Exception as e:
                    print(f"Router {self.router_id} failed to connect to Router {neighbor_id}: {e}")

    def send_message(self, sock, msg_type, payload=None):
        """Send a BGP message to a neighbor."""
        message = {"type": msg_type, "payload": payload}
        try:
            sock.sendall(json.dumps(message).encode())
        except BrokenPipeError:
            print(f"Error: Broken pipe when sending message to a neighbor.")
        except Exception as e:
            print(f"Error: {e}")

    def handle_neighbor_messages(self, neighbor_id, conn):
        """Handle messages from a connected neighbor."""
        while True:
            try:
                data = conn.recv(1024)
                if data:
                    message = json.loads(data.decode())
                    self.process_message(neighbor_id, message)
            except Exception as e:
                print(f"Error receiving data from Router {neighbor_id}: {e}")
                break

    def process_message(self, neighbor_id, message):
        """Process incoming BGP messages."""
        msg_type = message['type']
        if msg_type == BGP_KEEPALIVE:
            self.keepalive_received[neighbor_id] = time.time()
            print(f"Router {self.router_id} received KEEPALIVE from Router {neighbor_id}.")
        elif msg_type == BGP_UPDATE:
            if self.trust_model.decide_route(neighbor_id):
                print(f"Router {self.router_id} trusts Router {neighbor_id}, updating routing table.")
                self.update_routing_table(neighbor_id, message['payload'])
                self.propagate_routes(neighbor_id, message['payload'])
            else:
                print(f"Router {self.router_id} does not trust Router {neighbor_id}, ignoring update.")
        elif msg_type == BGP_WITHDRAW:
            print(f"Router {self.router_id} received route withdrawal from Router {neighbor_id}.")
            self.withdraw_routes(neighbor_id, message['payload'])

    def update_routing_table(self, neighbor_id, routes):
        """Update the routing table based on a neighbor's BGP UPDATE."""
        for route in routes:
            network = route['network']
            next_hop = neighbor_id
            as_path = route['as_path']
            existing_route = self.routing_table.get_route(network)
            if existing_route:
                if len(as_path) < len(existing_route['as_path']):
                    print(f"Router {self.router_id} updating existing route {network} via Router {neighbor_id}.")
                    self.routing_table.update_route(network, next_hop, as_path)
            else:
                print(f"Router {self.router_id} adding new route {network} via Router {neighbor_id}.")
                self.routing_table.add_route(network, next_hop, as_path)

    def propagate_routes(self, originating_neighbor, routes):
        """Propagate routes learned from one neighbor to all other neighbors."""
        for neighbor_id, sock in self.sockets.items():
            if neighbor_id != originating_neighbor:
                self.send_message(sock, BGP_UPDATE, routes)
                print(f"Router {self.router_id} propagated routes to Router {neighbor_id}. Routes: {routes}")

    def withdraw_routes(self, neighbor_id, routes):
        """Withdraw routes received from a neighbor."""
        for route in routes:
            network = route['network']
            self.routing_table.remove_route(network)
            print(f"Router {self.router_id} removed route {network} learned from Router {neighbor_id}.")
        for neighbor, sock in self.sockets.items():
            if neighbor != neighbor_id:
                self.send_message(sock, BGP_WITHDRAW, routes)
                print(f"Router {self.router_id} propagated route withdrawal to Router {neighbor}.")

    def send_keepalive(self):
        """Send KEEPALIVE messages to neighbors at regular intervals."""
        while True: 
            try:
                for neighbor_id, sock in self.sockets.items():
                    self.send_message(sock, BGP_KEEPALIVE)
                    print(f"Router {self.router_id} sent KEEPALIVE to Router {neighbor_id}.")
                time.sleep(KEEPALIVE_INTERVAL)
            except Exception as e:
                print(f"Error in keepalive thread: {e}")

    def check_for_neighbor_failures(self):
        """Periodically check if any neighbor has failed to send KEEPALIVE messages within the HOLD TIMER."""
        while True:
            try:
                current_time = time.time()
                for neighbor_id, last_keepalive_time in list(self.keepalive_received.items()):
                    if current_time - last_keepalive_time > HOLD_TIMER:
                        if neighbor_id not in self.down_routers:
                            print(f"Router {self.router_id} has not received KEEPALIVE from Router {neighbor_id}. Declaring Router {neighbor_id} as down.")
                            self.remove_neighbor_routes(neighbor_id)
                            self.down_routers.add(neighbor_id)
                            self.sockets.pop(neighbor_id, None)
                time.sleep(HOLD_TIMER)
            except Exception as e:
                print(f"Error during neighbor failure check: {e}")

    def remove_neighbor_routes(self, neighbor_id):
        """Remove routes learned from the failed neighbor."""
        print(f"Removing routes learned from Router {neighbor_id}.")
        routes_to_remove = []

        for route in self.routing_table.table[:]:
            print(f"Checking route: {route['next_hop']} is Router {neighbor_id}")
            if str(route['next_hop']).lower() == f"router{neighbor_id}".lower():
                print(f"Removing route for network: {route['network']}")
                routes_to_remove.append({"network": route['network']})
                self.routing_table.remove_route(route['network'])
            else:
                print(f"Route for network {route['network']} is not from Router {neighbor_id}.")
        
        if routes_to_remove:
            print(f"Propagating route withdrawals: {routes_to_remove}")
            self.propagate_route_withdrawal(neighbor_id, routes_to_remove)
        else:
            print(f"No routes found for removal from Router {neighbor_id}.")

    def propagate_route_withdrawal(self, neighbor_id, routes_to_remove):
        """Propagate route withdrawal to other neighbors."""
        for neighbor, sock in self.sockets.items():
            if neighbor != neighbor_id:
                self.send_message(sock, BGP_WITHDRAW, routes_to_remove)
                print(f"Router {self.router_id} propagated route withdrawal to Router {neighbor}.")

    def get_neighbor_by_ip(self, ip):
        """Get the neighbor ID by its IP address."""
        for neighbor_id in self.neighbors:
            if get_router_config(neighbor_id)['ip'] == ip:
                return neighbor_id
        return None

    def exchange_votes_with_neighbors(self):
        """Exchange votes with neighbors and update the trust model continuously."""
        while True:
            try:
                votes = self.voting_mechanism.exchange_votes()
                for neighbor_id, vote in votes.items():
                    if neighbor_id not in self.down_routers: #not casting to dead routers
                        self.trust_model.update_voted_trust(neighbor_id, vote)
                        print(f"Router {self.router_id} updated voted trust for Router {neighbor_id}: {vote}")
                time.sleep(30) 
            except Exception as e:
                print(f"Error in voting mechanism: {e}")

if __name__ == "__main__":
    router_id = int(os.getenv("ROUTER_ID"))
    bgp_router = BGP_Router(router_id)
    
    # Keep the main process alive
    #! I DONT KNOW WHY IS THISS. JUST DONT TOUCH THISSS
    # while True:
    #     time.sleep(1)