import pandas as pd
from itertools import product

# Step 1: Load the dataset
df = pd.read_csv('/Users/zahramousavi/Desktop/my subject/Idris data/prob_db.csv')

# Step 2: Identify blocks and split into certain and uncertain data
block_counts = df['block_id'].value_counts()
df['is_uncertain'] = df['block_id'].map(block_counts) > 1

# Split the data into certain and uncertain subsets
D_certain = df[df['is_uncertain'] == False].copy()
D_uncertain = df[df['is_uncertain'] == True].copy()


# print(f"Total Certain Data Rows: {len(D_certain)}")
# print(f"Total Uncertain Data Rows: {len(D_uncertain)}")
# print("\nCertain Data Sample:\n", D_certain.head())
# print("\nUncertain Data Sample:\n", D_uncertain.head(), "\n")

# Step 3: Identify missing features in uncertain data blocks
def identify_missing_features_per_block(block):
    """
    Identify which feature (A or B) is missing for the entire block.
    """
    # Check if the values in column A vary while B is constant
    if block['A'].nunique() > 1 and block['B'].nunique() == 1:
        return 'A'
    # Check if the values in column B vary while A is constant
    elif block['B'].nunique() > 1 and block['A'].nunique() == 1:
        return 'B'
    return None

# Apply the function to identify missing features for each block
missing_features = D_uncertain.groupby('block_id').apply(identify_missing_features_per_block)

# Assign the missing feature to all rows within each block
D_uncertain['missing_feature'] = D_uncertain['block_id'].map(missing_features)

# Print the results to verify the correct identification
# print(D_uncertain[['block_id', 'A', 'B', 'missing_feature']].drop_duplicates())

# Replace <block_id_number> with the specific block_id you want to check
#block_id_to_check = 89

# Filter the DataFrame to get the rows for that specific block_id
#result = D_uncertain[D_uncertain['block_id'] == block_id_to_check]

# Display the result to see which feature is missing for that block
#print(result[['block_id', 'A', 'B', 'missing_feature']])

# Step 4: Aggregate Queries for `A` and `B`
def compute_certain_sum(df, feature):
    """Calculate the aggregate sum for a given feature in certain data."""
    return df[feature].sum()


# Compute sum for certain data (constant)
certain_sum_A = compute_certain_sum(D_certain, 'A')
certain_sum_B = compute_certain_sum(D_certain, 'B')

#test Step 4
# print(f"Certain Sum for A: {certain_sum_A}")
# print(f"Certain Sum for B: {certain_sum_B}")


# Step 5: Calculate the domain of `A` and `B`, and count the blocks where each is missing
def get_domain_and_count(df, feature):
    """Get the domain of the feature and count the number of blocks where the feature is missing."""
    domain = df[df['missing_feature'] == feature][feature].unique()
    block_count = df[df['missing_feature'] == feature]['block_id'].nunique()
    return domain, block_count

domain_A, blocks_A_missing = get_domain_and_count(D_uncertain, 'A')
domain_B, blocks_B_missing = get_domain_and_count(D_uncertain, 'B')

# print(f"Domain of A: {domain_A}")
# print(f"Domain of B: {domain_B}")
# print(f"Blocks with A missing: {blocks_A_missing}")
# print(f"Blocks with B missing: {blocks_B_missing}")


# Step 6: Optimized Query Answering for Feature A
def find_best_world_iteratively(df, feature, domain, num_blocks, certain_sum):
    """
    Find the best possible world by comparing one world at a time to reduce memory usage.
    """
    blocks = df['block_id'].unique()
    best_world_sum = 0
    best_probability = 0

    # Iterate through all combinations of values in the domain for each block
    for world in product(domain, repeat=num_blocks):
        total_probability = 1
        world_sum = 0

        # Calculate the probability and sum for the current world
        for block_id, value in zip(blocks, world):
            selected_row = df[(df['block_id'] == block_id) & (df[feature] == value)]

            if not selected_row.empty:
                prob = selected_row['probability'].iloc[0]
                total_probability *= prob
                world_sum += value

        total_sum = world_sum + certain_sum

        # Update the best world if the current one has a higher probability
        if total_probability > best_probability:
            best_probability = total_probability
            best_world_sum = total_sum

    return best_world_sum, best_probability


# Apply the optimized function for A
best_sum_A, best_prob_A = find_best_world_iteratively(
    D_uncertain[D_uncertain['missing_feature'] == 'A'],
    'A',
    domain_A,
    blocks_A_missing,
    certain_sum_A
)

print(f"\nBest possible world for A: Sum(A) = {best_sum_A} with probability {best_prob_A}")

# Apply the optimized function for B
best_sum_B, best_prob_B = find_best_world_iteratively(
    D_uncertain[D_uncertain['missing_feature'] == 'B'],
    'B',
    domain_B,
    blocks_B_missing,
    certain_sum_B
)

print(f"Best possible world for B: Sum(B) = {best_sum_B} with probability {best_prob_B}")