import pandas as pd
from itertools import product
from collections import defaultdict

class DataSeparator:
    def __init__(self, file_path):
        self.file_path = '/Users/zahramousavi/Desktop/my subject/Idris data/prob_db.csv'
        self.data = None
        self.certain_data = None
        self.uncertain_data = None
        self.A_missing = None
        self.B_missing = None

    def load_data(self):
        self.data = pd.read_csv(self.file_path)
        print("Data loaded successfully.")

    def separate_data(self):
        if self.data is None:
            raise ValueError("Data not loaded. Please load the data first.")
        repeated_block_ids = self.data['block_id'].duplicated(keep=False)
        self.certain_data = self.data[~repeated_block_ids]
        self.uncertain_data = self.data[repeated_block_ids]
        print("Data separation completed.")

    def check_missingness(self):
        if self.uncertain_data is None:
            raise ValueError("Uncertain data not separated. Please run the 'separate_data()' method first.")
        grouped = self.uncertain_data.groupby('block_id')
        A_missing, B_missing = [], []
        for block_id, group in grouped:
            if group['A'].nunique() > 1:
                A_missing.append(group)
            if group['B'].nunique() > 1:
                B_missing.append(group)
        self.A_missing = pd.concat(A_missing) if A_missing else pd.DataFrame()
        self.B_missing = pd.concat(B_missing) if B_missing else pd.DataFrame()
        print(f"Uncertain data divided: {len(self.A_missing)} rows in A^m (A missing), {len(self.B_missing)} rows in B^m (B missing).")
        return self.A_missing, self.B_missing

    def create_blocks_in_A_missing(self):
        if self.A_missing is None or self.A_missing.empty:
            raise ValueError("A_missing data not available. Please run check_missingness() first.")
        self.A_missing = self.A_missing.sort_values(by=['block_id', 'A'])
        valid_blocks = []
        for block_id, group in self.A_missing.groupby('block_id'):
            if set(group['A']) == {1, 2, 3}:
                valid_blocks.append(group)
        self.A_missing_blocks = pd.concat(valid_blocks) if valid_blocks else pd.DataFrame()
        print("Blocks created in A_missing with unique values in column A.")
        return self.A_missing_blocks


class PossibleWorldsGenerator:
    def __init__(self, A_missing_blocks):
        self.blocks = [group for _, group in A_missing_blocks.groupby('block_id')]
        print(f"Identified {len(self.blocks)} unique blocks in A_missing.")

    def execute_sum_query(self):
        """
        Execute a sum query on 'A' for each possible world and aggregate probabilities for each unique sum.
        """
        query_results = defaultdict(float)
        total_combinations = 1

        for block in self.blocks:
            total_combinations *= len(block)

        print(f"Total possible worlds to consider: {total_combinations}")

        # Generate combinations in batches
        for world in product(*[block.itertuples(index=False, name=None) for block in self.blocks]):
            # Calculate the sum of 'A' values and world probability for the current world
            world_sum = sum(row[1] for row in world)  # Assuming 'A' is the second column
            world_prob = 1.0
            for row in world:
                world_prob *= row[-1]  # Assuming the probability is the last column

            # Aggregate probability for each unique sum
            query_results[world_sum] += world_prob

        # Identify the most probable sum
        max_sum = max(query_results, key=query_results.get)
        max_prob = query_results[max_sum]

        print("\nAggregated Query Results (Sum of A and corresponding probability):")
        for sum_val, prob in query_results.items():
            print(f"Sum: {sum_val}, Probability: {prob}")

        print(f"\nMost Probable Sum: {max_sum} with Probability: {max_prob}")

        return query_results, max_sum, max_prob


# Example usage:
if __name__ == "__main__":
    # Initialize the DataSeparator class with the file path
    file_path = '/path/to/your/prob_db.csv'  # Replace with your actual file path
    separator = DataSeparator(file_path)

    # Load the data
    separator.load_data()

    # Separate the data into certain and uncertain datasets
    separator.separate_data()

    # Check for missingness and divide the uncertain data
    A_missing, B_missing = separator.check_missingness()

    # Create blocks in the A_missing dataset with unique values in column A
    A_missing_blocks = separator.create_blocks_in_A_missing()

    # Initialize PossibleWorldsGenerator with A_missing_blocks and execute the queryy
    generator = PossibleWorldsGenerator(A_missing_blocks)
    query_results, max_sum, max_prob = generator.execute_sum_query()
