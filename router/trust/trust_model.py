class TrustModel:
    def __init__(self, direct_trust):
        """Initialize the trust model with a direct trust score."""
        self.direct_trust = direct_trust
        self.voted_trust = {}
    
    def update_voted_trust(self, neighbor_id, trust_value):
        """Update the voted trust for a neighbor based on the vote from other routers."""
        self.voted_trust[neighbor_id] = trust_value

    def calculate_total_trust(self, neighbor_id):
        """Calculate total trust as a combination of direct trust and voted trust."""
        if neighbor_id in self.voted_trust:
            return 0.6 * self.direct_trust + 0.4 * self.voted_trust[neighbor_id]
        return self.direct_trust

    def decide_route(self, neighbor_id):
        """Decide if the router should trust this neighbor for routing."""
        total_trust = self.calculate_total_trust(neighbor_id)
        if total_trust > 0.7: # Trust threshold
            return True
        return False