import pandas as pd
from itertools import product


class DataSeparator:
    def __init__(self, file_path):
        """
        Initialize the class with the file path to the dataset.
        """
        self.file_path = '/Users/zahramousavi/Desktop/my subject/Idris data/prob_db.csv'
        self.data = None
        self.certain_data = None
        self.uncertain_data = None
        self.A_missing = None
        self.B_missing = None

    def load_data(self):
        """
        Load the data from the CSV file.
        """
        self.data = pd.read_csv(self.file_path)
        print("Data loaded successfully.")

    def separate_data(self):
        """
        Separate the data into 'certain' and 'uncertain' datasets based on repeated block IDs.
        """
        if self.data is None:
            raise ValueError("Data not loaded. Please load the data first.")

        # Identify repeated block IDs
        repeated_block_ids = self.data['block_id'].duplicated(keep=False)

        # Separate the data into certain and uncertain based on repeated block_ids
        self.certain_data = self.data[~repeated_block_ids]  # Unique block IDs
        self.uncertain_data = self.data[repeated_block_ids]  # Repeated block IDs

        print("Data separation completed.")

    def check_missingness(self):
        """
        Check the missingness in columns A and B by comparing values within each block.
        Divide uncertain data into A^m and B^m based on inconsistent values.
        """
        if self.uncertain_data is None:
            raise ValueError("Uncertain data not separated. Please run the 'separate_data()' method first.")

        # Group by block_id
        grouped = self.uncertain_data.groupby('block_id')

        # Create two lists to store data where A or B is missing
        A_missing = []
        B_missing = []

        # Iterate through each block (group)
        for block_id, group in grouped:
            # Check if values in column A differ
            if group['A'].nunique() > 1:
                A_missing.append(group)
            # Check if values in column B differ
            if group['B'].nunique() > 1:
                B_missing.append(group)

        # Concatenate results into two DataFrames
        self.A_missing = pd.concat(A_missing) if A_missing else pd.DataFrame()
        self.B_missing = pd.concat(B_missing) if B_missing else pd.DataFrame()

        print(f"Uncertain data divided: {len(self.A_missing)} rows in A^m (A missing), {len(self.B_missing)} rows in B^m (B missing).")
        return self.A_missing, self.B_missing

    # def add_sequential_block_number(self, dataset):
    #     """
    #     Assign a unique block number to each unique block_id in the provided dataset (A_missing or B_missing)
    #     and add a new column 'block_number'.
    #     """
        # if dataset is None or dataset.empty:
        #     raise ValueError("The dataset provided is either empty or not defined.")

        # Get unique block_ids and assign sequential numbers
        # unique_blocks = dataset['block_id'].drop_duplicates().reset_index(drop=True)
        # unique_blocks = pd.DataFrame(unique_blocks, columns=['block_id'])
        # unique_blocks['block_number'] = range(1, len(unique_blocks) + 1)

        # Merge the sequential block number back into the dataset
        # dataset_with_block_numbers = pd.merge(dataset, unique_blocks, on='block_id')
        #
        # print("Sequential block number added to the provided dataset.")
        # return dataset_with_block_numbers

    def save_data(self):
        """
        Save the divided uncertain datasets with missing A or B columns.
        """
        if self.A_missing is not None and not self.A_missing.empty:
            self.A_missing.to_csv('A_missing.csv', index=False)
            print("A_missing data saved as 'A_missing.csv'")
        if self.B_missing is not None and not self.B_missing.empty:
            self.B_missing.to_csv('B_missing.csv', index=False)
            print("B_missing data saved as 'B_missing.csv'")

    def create_blocks_in_A_missing(self):
        """
        Create blocks in the A_missing dataset, where each block contains rows with unique values in column A (1, 2, and 3).
        """
        if self.A_missing is None or self.A_missing.empty:
            raise ValueError("A_missing data not available. Please run check_missingness() first.")

        # Sort A_missing by block_id and A to ensure values 1, 2, and 3 are grouped together within each block
        self.A_missing = self.A_missing.sort_values(by=['block_id', 'A'])

        # Initialize a list to store valid blocks
        valid_blocks = []

        # Group by block_id
        for block_id, group in self.A_missing.groupby('block_id'):
            # Check if the group contains exactly the values 1, 2, and 3 in column A
            if set(group['A']) == {1, 2, 3}:
                valid_blocks.append(group)

        # Concatenate all valid blocks into a DataFrame
        self.A_missing_blocks = pd.concat(valid_blocks) if valid_blocks else pd.DataFrame()

        print("Blocks created in A_missing with unique values in column A.")
        return self.A_missing_blocks


class PossibleWorldsGenerator:
    def __init__(self, A_missing_blocks):
        """
        Initialize the generator with blocks based on unique block_id.
        Automatically identifies block_ids and associated possible values.
        """
        # Group A_missing_blocks by block_id
        self.blocks = [group for _, group in A_missing_blocks.groupby('block_id')]
        print(f"Identified {len(self.blocks)} unique blocks in A_missing.")

    def generate_possible_worlds(self):
        """
        Generate all possible worlds by selecting one row from each block.
        """
        # Convert each block to a list of tuples (each row is a tuple containing values and probabilities)
        block_rows = [block.itertuples(index=False, name=None) for block in self.blocks]

        # Generate all combinations of selecting one row from each block
        possible_worlds = list(product(*block_rows))

        print(f"Total possible worlds generated: {len(possible_worlds)}")
        return possible_worlds

    def calculate_world_probability(self, world):
        """
        Calculate the probability of a single possible world by multiplying the probabilities
        from the probability column in each row of the world.
        """
        world_prob = 1.0
        for row in world:
            world_prob *= row[-1]  # Assuming the probability is the last column in each row
        return world_prob

    def execute_sum_query(self, possible_worlds):
        """
        Execute a sum query on 'A' for each possible world and calculate the probability of each sum.
        """
        results = []
        for world in possible_worlds:
            # Sum of values in 'A' for this world
            world_sum = sum(row[1] for row in world)  # Assuming 'A' is the second column
            world_prob = self.calculate_world_probability(world)
            results.append((world_sum, world_prob))

        # Aggregate probabilities for each unique sum result
        query_results = {}
        for world_sum, prob in results:
            if world_sum in query_results:
                query_results[world_sum] += prob
            else:
                query_results[world_sum] = prob

        # Identify the most probable sum and its probability
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

    # Add sequential block numbers for A_missing dataset
    # A_missing_with_block_numbers = separator.add_sequential_block_number(A_missing)

    # Add sequential block numbers for B_missing dataset
    # B_missing_with_block_numbers = separator.add_sequential_block_number(B_missing)

    # Save the updated datasets with block numbers
    # A_missing_with_block_numbers.to_csv('A_missing_with_block_number.csv', index=False)
    # B_missing_with_block_numbers.to_csv('B_missing_with_block_number.csv', index=False)

    # Create blocks in the A_missing dataset with unique values in column A
    A_missing_blocks = separator.create_blocks_in_A_missing()

    # Save the A_missing_blocks to a CSV file if needed
    # A_missing_blocks.to_csv('A_missing_blocks.csv', index=False)

    # print("A_missing blocks created and saved.")

    if not A_missing_blocks.empty:
        print(f"A_missing_blocks created with {len(A_missing_blocks)} rows.")
    else:
        print("A_missing_blocks is empty.")


    # Initialize PossibleWorldsGenerator with A_missing data and generate possible worlds
    generator = PossibleWorldsGenerator(A_missing_blocks)
    possible_worlds = generator.generate_possible_worlds()
    query_results, max_sum, max_prob = generator.execute_sum_query(possible_worlds)

