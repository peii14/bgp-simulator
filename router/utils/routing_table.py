class RoutingTable:
    def __init__(self, router_id):
        self.router_id = router_id
        self.table = []  # In-memory representation of the routing table

    def add_route(self, network, next_hop, as_path):
        """Add a new route to the routing table."""
        route = {
            "network": network,
            "next_hop": next_hop,
            "as_path": as_path
        }
        self.table.append(route)
        self.print_updated_routing_table()
        
    def remove_route(self, network):
        """Remove a route from the routing table based on the network."""
        removed = False
        for route in self.table:
            if route["network"] == network:
                print(f"Removing route for network: {network}")
                self.table.remove(route)
                removed = True
                print("\n--- Updated Routing Table for Router {self.router_id} ---")
                self.print_updated_routing_table()
                break
        if not removed:
            print(f"No route found for network {network} to remove.")

    def update_route(self, network, next_hop, as_path):
        """Update an existing route in the routing table."""
        updated = False
        for route in self.table:
            if route["network"] == network:
                route["next_hop"] = next_hop
                route["as_path"] = as_path
                updated = True
                self.print_updated_routing_table()
                break
        if not updated:
            print(f"No route found for network {network} to update.")

    def get_route(self, network):
        """Retrieve a route from the routing table based on the network."""
        for route in self.table:
            if route["network"] == network:
                return route
        return None

    def print_routing_table(self):
        """Print the current state of the routing table."""
        print(f"\n--- Initial Routing Table for Router {self.router_id} ---")
        if not self.table:
            print("Routing table is empty.")
        for route in self.table:
            print(f"Network: {route['network']}, Next Hop: {route['next_hop']}, AS Path: {route['as_path']}")
        print("--------------------------------------------\n")

    def print_updated_routing_table(self):
        """Print the updated state of the routing table after a change."""
        print(f"\n--- Updated Routing Table for Router {self.router_id} ---")
        if not self.table:
            print("Routing table is empty.")
        for route in self.table:
            print(f"Network: {route['network']}, Next Hop: {route['next_hop']}, AS Path: {route['as_path']}")
        print("--------------------------------------------\n")