class TrustModel:
    def __init__(self, direct_trust, trust_threshold=0.4, direct_weight=0.6, voted_weight=0.4):
        """Initialize the trust model with direct trust, weights for trust calculation, and a trust threshold."""
        self.direct_trust = direct_trust
        self.voted_trust = {}
        self.trust_threshold = trust_threshold
        self.direct_weight = direct_weight
        self.voted_weight = voted_weight

    def update_voted_trust(self, neighbor_id, trust_value):
        """Update the voted trust for a neighbor based on the vote from other routers."""
        self.voted_trust[neighbor_id] = trust_value
        print(f"Voted trust for Router {neighbor_id} updated to {trust_value}")

    def calculate_total_trust(self, neighbor_id):
        """Calculate total trust as a combination of direct trust and voted trust."""
        voted_trust = self.voted_trust.get(neighbor_id, 0)
        total_trust = (self.direct_weight * self.direct_trust) + (self.voted_weight * voted_trust)
        print(f"Total trust for Router {neighbor_id}: {total_trust} (Direct: {self.direct_trust}, Voted: {voted_trust})")
        return total_trust

    def decide_route(self, neighbor_id):
        """Decide if the router should trust this neighbor for routing."""
        total_trust = self.calculate_total_trust(neighbor_id)
        print(f"Total trust for Router {neighbor_id}: {total_trust}")
        if total_trust > self.trust_threshold:
            print(f"Trust decision for Router {neighbor_id}: TRUSTED")
            return True
        print(f"Trust decision for Router {neighbor_id}: NOT TRUSTED")
        return False

    def decay_trust_over_time(self, neighbor_id, decay_rate=0.01):
        """Decay the trust score for a neighbor over time if there are no interactions."""
        if neighbor_id in self.voted_trust:
            self.voted_trust[neighbor_id] = max(0, self.voted_trust[neighbor_id] - decay_rate)
            print(f"Trust for Router {neighbor_id} decayed to {self.voted_trust[neighbor_id]}")