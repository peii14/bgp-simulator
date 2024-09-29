import json

# Load the JSON data
def load_trust_json(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    trust_table_scores = {}  #Trust scores from JSON

    # Iterate over all routers in the JSON
    for router in data['routers']:
        router_id = f"R{router['id']}"  #print routers ID
        neighbors = router['neighbors']
        direct_trust = router['trust']['direct_trust']

        # writting the router in the trust_table_scores
        trust_table_scores[router_id] = {}

        # Adding the score from above
        for neighbor in neighbors:
            neighbor_id = f"R{neighbor}"  # Add the neighbor as 'R' + ID
            trust_table_scores[router_id][neighbor_id] = direct_trust

    return trust_table_scores

json_file_path = '../config.json' 
trust_table_scores = load_trust_json(json_file_path)  # Consistent variable name

print(trust_table_scores)  # Print the trust tablee
