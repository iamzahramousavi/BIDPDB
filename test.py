import pandas as pd

# Load the original CSV file
df = pd.read_csv('/Users/zahramousavi/Desktop/My Files/Fall2024/BIDP/prob_db.csv')

# Select the first 31 rows
df_first_31 = df.head(31)

# Save the new data to a new CSV file
df_first_31.to_csv('new_data.csv', index=False)
