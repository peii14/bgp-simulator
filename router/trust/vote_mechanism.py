import random

class VotingMechanism:
    def __init__(self, router_id, neighbors):
        """Initialize the voting mechanism for a router."""
        self.router_id = router_id
        self.neighbors = neighbors
        self.votes = {}

    def cast_vote(self, neighbor_id):
        """Cast a vote for a neighbor, either trusting them or not."""
        vote = random.uniform(0.5, 1.0)  # Randomly generate a trust score between 0.5 and 1.0
        self.votes[neighbor_id] = vote
        print(f"Router {self.router_id} cast vote for Router {neighbor_id}: {vote}")
        return vote

    def exchange_votes(self):
        """Exchange votes with neighbors and return the results."""
        votes_result = {}
        for neighbor in self.neighbors:
            vote = self.cast_vote(neighbor)
            votes_result[neighbor] = vote
        return votes_result

    def receive_votes(self, votes_from_others):
        """Receive votes from other routers and update local trust values."""
        for neighbor_id, vote in votes_from_others.items():
            print(f"Router {self.router_id} received vote from Router {neighbor_id}: {vote}")