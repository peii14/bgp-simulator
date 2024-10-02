# TODO: Enhance and Implement the trust model for the router to decide if it should trust a neighbor for routing.
class TrustModel:
    def __init__(self, distances):
        self.distances = distances  # data from config.json
        self.voted_trust = {}  # Store voted trust from other routers

    def update_voted_trust(self, neighbor_id, trust_value):
        """Update the voted trust for a neighbor based on the vote from other routers."""
        self.voted_trust[neighbor_id] = trust_value

    def decide_best_route(self):
        """Decide which neighbor to trust based on the shortest distance and voted trust."""
        if not self.distances:
            return None  # No neighbors available

        # Blend both distance and voted trust
        for neighbor, trust in self.voted_trust.items():
            if neighbor in self.distances:
                self.distances[neighbor] = 0.6 * self.distances[neighbor] + 0.4 * trust

        # Choose the neighbor with the smallest distance
        best_neighbor = min(self.distances, key=self.distances.get)
        return best_neighbor
