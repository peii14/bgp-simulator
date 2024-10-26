class TrustModel:
    def __init__(self, direct_trust, direct_weight=0.6, voted_weight=0.4):
        """Initialize the trust model with direct trust, weights for trust calculation, and a trust threshold."""
        self.direct_trust = direct_trust
        self.indirect_voted_trust = {}
        self.direct_weight = direct_weight
        self.indirect_voted_weight = voted_weight

    def update_voted_trust(self, neighbor_id, vote):
        """Update trust scores based on votes."""
        if neighbor_id not in self.indirect_voted_trust:
            self.indirect_voted_trust[neighbor_id] = 0

        if vote == 'trusted':
            self.indirect_voted_trust[neighbor_id] += 0.1
        elif vote == 'untrusted':
            self.indirect_voted_trust[neighbor_id] -= 0.1
        else:
            print(f"Unexpected vote value: {vote} from Router {neighbor_id}")
            return

            # Normalize the value between 0 and 10
        self.indirect_voted_trust[neighbor_id] = max(0.0, min(1.0, self.indirect_voted_trust[neighbor_id]))


    def get_trust_score(self, neighbor_id):
        """Get the trust score of a neighbor."""
        return self.calculate_total_trust(neighbor_id)

    def calculate_total_trust(self, neighbor_id):
        """Calculate total trust as a combination of direct trust and voted trust."""
        direct = self.direct_trust.get(neighbor_id, 0)
        voted = self.indirect_voted_trust.get(neighbor_id, 0)
        total_trust = (self.direct_weight * direct) + (self.indirect_voted_weight * voted)
        print(f"Total trust for Router {neighbor_id}: {total_trust} (Direct: {direct}, Voted: {voted})")
        return total_trust


    def decay_trust_over_time(self, neighbor_id, decay_rate=0.01):
        """Decay the trust score for a neighbor over time if there are no interactions."""
        if neighbor_id in self.indirect_voted_trust:
            self.indirect_voted_trust[neighbor_id] = max(0, self.indirect_voted_trust[neighbor_id] - decay_rate)
            print(f"Trust for Router {neighbor_id} decayed to {self.indirect_voted_trust[neighbor_id]}")