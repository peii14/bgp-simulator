import json
import socket
import threading
import time
import sys
from lib2to3.btm_utils import rec_test

from utils.routing_table import RoutingTable
from trust.trust_model import TrustModel
from trust.vote_mechanism import VotingMechanism
from utils.packet_processing import create_ip_packet, parse_ip_packet
import os


# Load the configuration from config.json
with open('config.json') as config_file:
    config = json.load(config_file)

# Helper function to get the router's configuration based on its ID
def get_router_config(router_id):
    for router in config['routers']:
        if router['id'] == router_id:
            return router
    return None

BGP_OPEN = "OPEN"
BGP_KEEPALIVE = "KEEPALIVE"
BGP_UPDATE = "UPDATE"
BGP_NOTIFICATION = "NOTIFICATION"

HOLD_TIMER = config['bgp_defaults']['hold_timer']
KEEPALIVE_INTERVAL = config['bgp_defaults']['keepalive_interval']

class BGP_Router:
    def __init__(self, router_id):
        self.config = get_router_config(router_id)
        if not self.config:
            print(f"Router ID {router_id} not found in config.")
            sys.exit(1)

        self.router_id = self.config['id']
        self.ip = self.config['ip']
        self.neighbors = self.config['neighbors']
        self.routing_table = RoutingTable(self.router_id)
        self.trust_model = TrustModel(self.config['trust']['direct_trust'])
        self.voting_mechanism = VotingMechanism(self.router_id, self.neighbors)
        self.sockets = {}
        self.keepalive_received = {}

        # Start the router
        self.start_router()

    def start_router(self):
        listener_thread = threading.Thread(target=self.listen_for_neighbors)
        listener_thread.daemon = True
        listener_thread.start()

        time.sleep(2)  # Sleep for a while to ensure all routers are up
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

    def listen_for_neighbors(self):
        """Listen for connections from neighbor routers."""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.ip, 179))  
        server_socket.listen(5)
        print(f"Router {self.router_id} is listening for neighbors on {self.ip}...")

        while True:
            conn, addr = server_socket.accept()
            neighbor_id = self.get_neighbor_by_ip(addr[0])
            if neighbor_id:
                print(f"Router {self.router_id} accepted connection from Router {neighbor_id}.")
                self.sockets[neighbor_id] = conn
                self.keepalive_received[neighbor_id] = time.time()

                # Start a thread to handle incoming messages from this neighbor
                threading.Thread(target=self.handle_neighbor_messages, args=(neighbor_id, conn)).start()

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
        sock.sendall(json.dumps(message).encode())

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
        if message['type'] == BGP_KEEPALIVE:
            self.keepalive_received[neighbor_id] = time.time()
            print(f"Router {self.router_id} received KEEPALIVE from Router {neighbor_id}.")

        elif message['type'] == BGP_UPDATE:
            if self.trust_model.decide_route(neighbor_id):
                print(f"Router {self.router_id} trusts Router {neighbor_id}, updating routing table.")
                self.update_routing_table(neighbor_id, message['payload'])
            else:
                print(f"Router {self.router_id} does not trust Router {neighbor_id}, ignoring update.")

        elif message['type'] == BGP_OPEN:
            print(f"Router {self.router_id} received OPEN message from Router {neighbor_id}.")

        elif message['type'] == BGP_NOTIFICATION:
            print(f"Router {self.router_id} received NOTIFICATION from Router {neighbor_id}.")

    def send_keepalive(self):
        """Send KEEPALIVE messages to neighbors at regular intervals."""
        while True:
            for neighbor_id, sock in self.sockets.items():
                try:
                    self.send_message(sock, BGP_KEEPALIVE)
                    print(f"Router {self.router_id} sent KEEPALIVE to Router {neighbor_id}.")
                except Exception as e:
                    print(f"Error sending KEEPALIVE to Router {neighbor_id}: {e}")
            time.sleep(KEEPALIVE_INTERVAL)

    def update_routing_table(self, neighbor_id, routes):
        # TODO: Implement the routing table update logic here
        """Update the routing table based on a neighbor's update."""
        #self.routing_table[neighbor_id] = routes #here the route is a message?
        #self.routing_table.update_route(network, neighbor_id, as_path) OR routes
        print(f"Router {self.router_id} updated routing table with routes from Router {neighbor_id}.")

    def check_for_neighbor_failures(self):
        """Periodically check if any neighbor has failed to send KEEPALIVE messages within the HOLD TIMER."""
        while True:
            current_time = time.time()
            for neighbor_id, last_keepalive_time in self.keepalive_received.items():
                if current_time - last_keepalive_time > HOLD_TIMER:
                    print(f"Router {self.router_id} has not received KEEPALIVE from Router {neighbor_id}. Declaring Router {neighbor_id} as down.")
                    self.remove_neighbor_routes(neighbor_id)
            time.sleep(HOLD_TIMER)

    def remove_neighbor_routes(self, neighbor_id):
        """Remove routes learned from the failed neighbor."""
        if self.routing_table.is_route_in_routing_table(neighbor_id):
            self.routing_table.remove_route(neighbor_id)
            print(f"Router {self.router_id} removed routes from Router {neighbor_id} in the routing table.")

    def get_neighbor_by_ip(self, ip):
        """Get the neighbor ID by its IP address."""
        for neighbor_id in self.neighbors:
            if get_router_config(neighbor_id)['ip'] == ip:
                return neighbor_id
        return None

    def exchange_votes_with_neighbors(self):
        """Exchange votes with neighbors and update trust model."""
        while True:
            votes = self.voting_mechanism.exchange_votes()
            
            for neighbor_id, vote in votes.items():
                self.trust_model.update_voted_trust(neighbor_id, vote)
                print(f"Router {self.router_id} updated voted trust for Router {neighbor_id}: {vote}")
            
            time.sleep(30)  

if __name__ == "__main__":
    router_id = int(os.getenv("ROUTER_ID"))
    bgp_router = BGP_Router(router_id)
    