import json

with open('config.json') as config_file:
    routing_table_config = json.load(config_file)


class RoutingTable:
    def __init__(self, router_id):
        self.table = []
        self.load_from_config(router_id)

    def load_from_config(self, router_id):
        for router in routing_table_config['routers']:
            if router['id'] == router_id:
                for entry in router['routing_table']:
                    self.add_route(entry['network'], entry['next_hop'], entry['as_path'])
                    print(f"Adding route from config: {entry['network']} -> Router {entry['next_hop']} with AS path: {entry['as_path']}")


    def add_route(self, network, next_hop, as_path):
        """Add a new route to the routing_table"""
        route = {
            "network": network,
            "next_hop": next_hop,
            "as_path": as_path
        }
        self.table.append(route)


    def remove_route(self, next_hop):
        """Remove a route from the routing table based on the network"""
        for route in self.table:
            if route["next_hop"] == next_hop:
                self.table.remove(route)
                print(f"Route removed: {next_hop}")


    def get_route_by_next_hop(self, next_hop):
        """Retrieve a route from the routing table based on the next_hop"""
        for route in self.table:
            if route["next_hop"] == next_hop:
                return route
        return None

    def is_route_in_routing_table(self, next_hop):
        """Check if any route has the given next_hop."""
        for route in self.table:
            if route['next_hop'] == next_hop:
                return True
        return False

    def update_route(self, network, next_hop, as_path):
        """Update an existing route in the routing table"""
        for route in self.table:
            if route["network"] == network:
                route["next_hop"] = next_hop
                route["as_path"] = as_path
                print(f"Route updated: {network} -> {next_hop}")
                break