import json

import pandas as pd

# Load the JSON data
with open("data.json") as json_file:
    data = json.load(json_file)

# Convert JSON data to a DataFrame
df = pd.json_normalize(data)

# Export DataFrame to Excel
df.to_excel("data.xlsx", index=False)
