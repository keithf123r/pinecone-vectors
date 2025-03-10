import os
from dotenv import load_dotenv
import pandas as pd
from pinecone import Pinecone

# Load environment variables from .env file
load_dotenv()

# Initialize the Pinecone client
pc = Pinecone(api_key=os.environ.get('PINECONE_API_KEY'))

# Connect to your index
index = pc.Index(os.environ.get('PINECONE_INDEX'))

# Fetch all records
all_ids = []
for ids in index.list(namespace=os.environ.get('PINECONE_NAMESPACE')):
    all_ids.extend(ids)

batch_size = 100
all_records = []

for i in range(0, len(all_ids), batch_size):
    batch_ids = all_ids[i:i+batch_size]
    batch_records = index.fetch(ids=batch_ids)
    all_records.extend(batch_records['vectors'].values())
    print(f"Fetched {len(batch_records['vectors'])} records")

# Convert the fetched records to a pandas DataFrame
df = pd.DataFrame(all_records)

# Save the DataFrame to a CSV file
df.to_csv('pinecone_records.csv', index=False)

