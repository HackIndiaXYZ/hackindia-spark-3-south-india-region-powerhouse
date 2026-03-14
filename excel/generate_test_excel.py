import pandas as pd

data = [
    { "rollno": "23UAI002", "name": "ABBHISHEK BEHERA", "avg_score": None }, 
    { "rollno": "23UAI003", "name": "ABDULKALAM J", "avg_score": None },
    { "rollno": "23UAI004", "name": "ABIESWAR T", "avg_score": 85.5 }, # Added a score to test non-empty
    { "rollno": "23UAI006", "name": "AISVA MALAR A", "avg_score": None }
]

df = pd.DataFrame(data)
df.to_excel('test_data.xlsx', index=False)
print("Created test_data.xlsx")
