## Overview
This project implements an optimized query answering system for Block Independent Probabilistic Database(BIPDB). The goal is to efficiently answer aggregate queries by leveraging probabilistic inference on uncertain data to achieve the most probable answer of aggreagte queries.
## Requirements
Make sure you have Python 3.x installed, with the Dependencies:
- pandas
- itertools
## How to Run
1. **Place your dataset**: Ensure your dataset is saved as `prob_db.csv` in the project folder.
2. **Run the script**: python main.py
3. The script will output:
- The domains of attributes `A` and `B`.
- The number of uncertain blocks.
- The best possible worlds for attributes `A` and `B` with their probabilities.
- The optimized aggregate query results.
## Methodology
1. **Data Separation**:
- Separate rows into `Certain Data` (rows with unique `block_id`) and `Uncertain Data` (rows with repeated `block_id` indicating missing values).
2. **Block Creation**:
- For each uncertain block, identify which attribute (`A` or `B`) is missing and assign possible values with their associated probabilities.
3. **Possible Worlds**:
- Determine the domain of possible values for each missing attribute and calculate the number of uncertain blocks to find the number of possible worlds.
4. **Optimized Query Answering**:
- Use an iterative approach to generate possible worlds, calculate aggregate sums, and select the world with the highest probability.
- This reduces memory usage by avoiding the generation of all possible worlds simultaneously.
## Troubleshooting
- If the script takes too long to run, consider adjusting the dataset size or the number of uncertain blocks. 
