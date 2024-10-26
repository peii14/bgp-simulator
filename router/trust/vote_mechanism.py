import random
# TODO: Enhance and Implement the VotingMechanism class
class VotingMechanism:
    def __init__(self, router_id, neighbors):
        """Initialize the voting mechanism for a router."""
        self.router_id = router_id
        self.neighbors = neighbors
        self.votes = {}

    def cast_vote(self, neighbor_id, as_path):
        """Cast a vote for a neighbor, either trusting them or not."""
       # vote = random.uniform(0.5, 1.0)  # Randomly generate a trust score between 0.5 and 1.0

        vote = 'trusted' if len(as_path) < 4 else 'untrusted'
        self.votes[neighbor_id] = vote
        # print(f"Router {self.router_id} cast vote for Router {neighbor_id}: {vote}")
        return vote

    def exchange_votes(self, routing_table):
        """Simulate the exchange of votes with neighbors."""
        votes_result = {}
        for neighbor_id in self.neighbors:
            for route in routing_table.table:
                vote = self.cast_vote(neighbor_id, route['as_path'])
                votes_result[neighbor_id] = vote
                print(f"{self.router_id} votes {vote} for {neighbor_id} with AS path: {route['as_path']}")
        return votes_result

    def receive_votes(self, votes_from_others):
        """Receive votes from other routers and update local trust values."""
        for neighbor_id, vote in votes_from_others.items():
            print(f"Router {self.router_id} received vote from Router {neighbor_id}: {vote}")