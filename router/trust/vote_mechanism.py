import random
# TODO: Enhance and Implement the VotingMechanism class
class VotingMechanism:
    def __init__(self, router_id, neighbors):  # initializing each router, storing routers id and neigbours
        self.router_id = router_id
        self.neighbors = neighbors
        self.votes = {}

    def cast_vote(self, neighbor_id): # creating votes for neighbours
        vote = random.uniform(0.5, 1.0)  # Generating random score between 0.5 and 1.0, we can change it into something more complicated if we think we need to.
        self.votes[neighbor_id] = vote
        print(f"Router {self.router_id} cast vote for Router {neighbor_id}: {vote}")
        return vote

    def exchange_votes(self):
        """Exchange votes with neighbors and return the results."""
        votes_result = {}
        for neighbor in self.neighbors:
            vote = self.cast_vote(neighbor)
            votes_result[neighbor] = vote # Returns the votes_result dictionary containing all the votes cast for neighbors.
        return votes_result