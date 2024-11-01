import pandas as pd

df = pd.read_csv('data/data.csv')
df = df.sort_values('building')

# Try to drop each column individually
columns_to_drop = ['instructor_name', 'department', 'delivery_method', 'division']
for col in columns_to_drop:
    if col in df.columns:
        df = df.drop(columns=[col])
    else:
        print(f"Column '{col}' not found in DataFrame")

df.to_csv('data/data.csv', index=False)