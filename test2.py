import pandas as pd
from itertools import product

# Sample data extracted from your input file
df = pd.read_csv('/Users/zahramousavi/Desktop/My Files/Fall2024/BIDP/prob_db.csv')

# Assume certain_sum_A is zero as it's not given in the dataset
certain_sum_A = 0

# Extract the domains and probabilities for blocks 12 and 25
domain_12 = df[df['block_id'] == 12][['A', 'probability']].values
domain_25 = df[df['block_id'] == 25][['A', 'probability']].values

# Generate all possible worlds (3^2 = 9 possible worlds)
possible_worlds = list(product(domain_12, domain_25))

# Prepare the result table
results = []
for world in possible_worlds:
    T12_value, T12_prob = world[0]
    T25_value, T25_prob = world[1]

    # Calculate uncertain sum and total probability for each world
    uncertain_sum = T12_value + T25_value + certain_sum_A
    total_prob = T12_prob * T25_prob

    # Store the result
    results.append({
        'T12': T12_value,
        'T25': T25_value,
        'Q(W_k)': uncertain_sum,
        'Probability': total_prob
    })

# Convert the results into a DataFrame
results_df = pd.DataFrame(results)

# Display the DataFrame
print("Possible Worlds Table:")
print(results_df)

# Save the results to a CSV file
csv_path = "possible_worlds.csv"
results_df.to_csv(csv_path, index=False)
print(f"\nResults have been saved to {csv_path}")
