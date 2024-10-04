import json

class RoutingTable:
    def __init__(self):
        self.table = []

with open('config.json') as config_file:
    config = json.load(config_file)

def load_from_config(self, routing_table_config):
    for router in routing_table_config['routers']:
        for entry in router['routing_table']:
            self.add_route(entry['network'], entry['next_hop'], entry['as_path'])

def add_route(self, network, next_hop, as_path):
    """Add a new route to the routing_table"""
    route = {
        "network": network,
        "next_hop": next_hop,
        "as_path": as_path
    }
    self.table.append(route)
    print(f"Route added: {network} -> {next_hop}")


def remove_route(self, network):
    """Remove a route from the routing table based on the network"""
    for route in self.table:
        if route["network"] == network:
             self.table.remove(route)
    print(f"Route removed: {network}")

def get_route(self, network):
    """Retrieve a route from the routing table based on the network"""
    for route in self.table:
        if route["network"] == network:
            return route
    return None

def update_route(self, network, next_hop, as_path):
    """Update an existing route in the routing table"""
    for route in self.table:
        if route["network"] == network:
            route["next_hop"] = next_hop
            route["as_path"] = as_path
            print(f"Route updated: {network} -> {next_hop}")
            break