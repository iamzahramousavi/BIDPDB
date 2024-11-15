import pandas as pd
from itertools import product

# Load the dataset
df = pd.read_csv('/Users/zahramousavi/Desktop/My Files/Fall2024/BIDP/prob_db.csv')

# Identify blocks and split into certain and uncertain data
block_counts = df['block_id'].value_counts()
df['is_uncertain'] = df['block_id'].map(block_counts) > 1

# Split data into certain and uncertain subsets
D_certain = df[df['is_uncertain'] == False].copy()
D_uncertain = df[df['is_uncertain'] == True].copy()


# Identify missing features in uncertain data blocks
def identify_missing_features_per_block(block):
    if block['A'].nunique() > 1 and block['B'].nunique() == 1:
        return 'A'
    elif block['B'].nunique() > 1 and block['A'].nunique() == 1:
        return 'B'
    return None


missing_features = D_uncertain.groupby('block_id').apply(identify_missing_features_per_block)
D_uncertain['missing_feature'] = D_uncertain['block_id'].map(missing_features)


def compute_certain_sum(df, feature):
    return df[feature].sum()


certain_sum_A = compute_certain_sum(D_certain, 'A')


# Get domain and count of blocks with missing values
def get_domain_and_count(df, feature):
    domain = df[df['missing_feature'] == feature][feature].unique()
    block_count = df[df['missing_feature'] == feature]['block_id'].nunique()
    return domain, block_count


domain_A, blocks_A_missing = get_domain_and_count(D_uncertain, 'A')


# Function to generate all possible worlds and save results
def save_all_possible_worlds(df, feature, domain, num_blocks, certain_sum, output_csv):
    blocks = df['block_id'].unique()
    results = []

    # Debug: Print the number of blocks and domain
    print(f"Blocks: {blocks}")
    print(f"Domain for {feature}: {domain}")

    for world in product(domain, repeat=num_blocks):
        total_probability = 1
        world_sum = 0
        world_assignment = {}

        for block_id, value in zip(blocks, world):
            selected_row = df[(df['block_id'] == block_id) & (df[feature] == value)]

            # If no matching row is found, log it for debugging
            if selected_row.empty:
                print(f"Warning: No match found for block {block_id} with {feature}={value}")
                continue

            prob = selected_row['probability'].iloc[0]
            total_probability *= prob
            world_sum += value
            world_assignment[f"T{block_id}"] = value

        total_sum = world_sum + certain_sum
        world_assignment['Q(W_k)'] = total_sum
        world_assignment['Probability'] = total_probability
        results.append(world_assignment)

    # Convert to DataFrame and save to CSV
    results_df = pd.DataFrame(results)
    print(f"Generated {len(results_df)} worlds")
    results_df.to_csv(output_csv, index=False)
    return results_df


# Generate possible worlds for A and save to CSV
csv_path_A = '/Users/zahramousavi/Desktop/My Files/Fall2024/BIDP/possible_worlds_A.csv'
results_A = save_all_possible_worlds(
    D_uncertain[D_uncertain['missing_feature'] == 'A'],
    'A',
    domain_A,
    blocks_A_missing,
    certain_sum_A,
    csv_path_A
)

print("\nSample of Possible Worlds for A:")
print(results_A.head(10))
