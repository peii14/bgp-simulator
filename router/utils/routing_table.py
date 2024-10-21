import json
import os

class RoutingTable:
    def __init__(self, router_id, file_path='routing_table.json'):
        self.router_id = router_id
        self.table = []
        self.file_path = file_path
        self.load_routing_table()

    def load_routing_table(self):
        """Load routing table from a JSON file, if it exists."""
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                self.table = json.load(file)
                print(f"Routing table loaded for Router {self.router_id}.")

    def save_routing_table(self):
        """Save the current routing table to a JSON file."""
        with open(self.file_path, 'w') as file:
            json.dump(self.table, file, indent=4)
        print(f"Routing table saved for Router {self.router_id}.")

    def add_route(self, network, next_hop, as_path):
        """Add a new route to the routing table."""
        route = {
            "network": network,
            "next_hop": next_hop,
            "as_path": as_path
        }
        self.table.append(route)
        print(f"Route added: {network} -> {next_hop}")
        self.save_routing_table()
        self.print_routing_table()

    def remove_route(self, network):
        """Remove a route from the routing table based on the network."""
        removed = False
        for route in self.table:
            if route["network"] == network:
                self.table.remove(route)
                removed = True
                print(f"Route removed: {network}")
                self.save_routing_table()
                self.print_routing_table()
                break
        if not removed:
            print(f"No route found for network {network} to remove.")

    def get_route(self, network):
        """Retrieve a route from the routing table based on the network."""
        for route in self.table:
            if route["network"] == network:
                return route
        return None

    def update_route(self, network, next_hop, as_path):
        """Update an existing route in the routing table."""
        updated = False
        for route in self.table:
            if route["network"] == network:
                route["next_hop"] = next_hop
                route["as_path"] = as_path
                updated = True
                print(f"Route updated: {network} -> {next_hop}")
                self.save_routing_table()
                self.print_routing_table()
                break
        if not updated:
            print(f"No route found for network {network} to update.")

    def print_routing_table(self):
        """Print the current state of the routing table."""
        print(f"\n--- Current Routing Table for Router {self.router_id} ---")
        for route in self.table:
            print(f"Network: {route['network']}, Next Hop: {route['next_hop']}, AS Path: {route['as_path']}")
        print("--------------------------------------------\n")