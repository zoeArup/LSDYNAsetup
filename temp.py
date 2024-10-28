import os
import numpy as np
import re
import time
import scipy
import pandas as pd


import pandas as pd

import pandas as pd

# Sample DataFrame
data = {
    'x': [1, 2, 2, 3, 3, 3],
    'y': [4, 5, 5, 6, 6, 6],
    'z': [7, 8, 9, 10, 11, 12]
}
df = pd.DataFrame(data)

def rows_min_max_grouped_by_x(df):
    min_rows = df.loc[df.groupby('x')['y'].idxmin()]
    max_rows = df.loc[df.groupby('x')['y'].idxmax()]
    return pd.concat([min_rows, max_rows])

def rows_min_max_grouped_by_y(df):
    min_rows = df.loc[df.groupby('y')['x'].idxmin()]
    max_rows = df.loc[df.groupby('y')['x'].idxmax()]
    return pd.concat([min_rows, max_rows])

grouped_by_x = rows_min_max_grouped_by_x(df)
grouped_by_y = rows_min_max_grouped_by_y(df)
# Combine the results
result = pd.concat([grouped_by_x, grouped_by_y]).drop_duplicates()

result = result.sort_values(by=['x', 'y']).reset_index(drop=True)
result['i']=range(len(result)); result['i']=result['i']+1000
for i in range(0, 4):
    result[f'z{i+1}'] = result['z'] - (0.5 * i)
    result[f'i{i+1}'] = result['i']*(i+1)

shell=result.copy()
for i in range(0, 4):
    shell[f'z{i+1}+1'] = shell[f'i{i+1}']
    shell[f'i{i+1}+1'] = shell[f'z{i+1}']


print(result)

extensive_df = pd.DataFrame()
for i in range(1, 5):
    temp_df = result[['x', 'y', f'z{i}', f'i{i}']].rename(columns={f'z{i}': 'z', f'i{i}': 'i'})
    extensive_df = pd.concat([extensive_df, temp_df])

# Reset index for the final DataFrame
extensive_df = extensive_df.reset_index(drop=True)

print(extensive_df)


import pandas as pd

# Sample dataframe with a series of strings
data = {
    'A': ['apple orange banana', 'grape apple mango', 'banana orange grape', 'apple banana grape', 'mango grape orange']
}

df = pd.DataFrame(data)

# Decompose the column into columns by space
df[['B', 'C', 'D']] = df['A'].str.split(' ', expand=True)

# Count the number of duplicated values in columns B, C, D
duplicated_counts = pd.concat([df['B'], df['C'], df['D']]).value_counts()

# Take away the values that appear 4 times
values_to_remove = duplicated_counts[duplicated_counts == 4].index.tolist()

# Get the indices of rows where any of the values in columns B, C, D appear in values_to_remove
indices_to_keep = df[~df[['B', 'C', 'D']].isin(values_to_remove).any(axis=1)].index.tolist()

# Sample another dataframe
data2 = {
    'X': [10, 20, 30, 40, 50],
    'Y': [100, 200, 300, 400, 500]
}

df2 = pd.DataFrame(data2)

# Obtain only the rows with index appear in the list
result_df = df2.loc[indices_to_keep]

print("Indices to keep:", indices_to_keep)
print("Resulting dataframe:")
print(result_df)
