import os
from dotenv import load_dotenv
import pandas as pd
from pinecone import Pinecone

# Load environment variables from .env file
load_dotenv()

# Initialize the Pinecone client
pc = Pinecone(api_key=os.environ.get('PINECONE_API_KEY'))

# Connect to your index
index_name = os.environ.get('PINECONE_INDEX')
index = pc.Index(index_name)
namespace = os.environ.get('PINECONE_NAMESPACE')

print(f"Connected to index: {index_name}")
print(f"Using namespace: {namespace}")

# Fetch all vector IDs
all_ids = []
try:
    # In the newer Pinecone SDK, list() returns a generator
    # We need to iterate through the generator to get all IDs
    list_generator = index.list(namespace=namespace)
    
    # Iterate through the generator
    batch_count = 0
    for batch in list_generator:
        batch_count += 1
        # Convert batch to list if it's not already
        batch_ids = list(batch) if not isinstance(batch, list) else batch
        print(f"Retrieved batch {batch_count} with {len(batch_ids)} IDs")
        all_ids.extend(batch_ids)
        
except Exception as e:
    print(f"Error retrieving vector IDs: {e}")
    
print(f"Total IDs retrieved: {len(all_ids)}")

if len(all_ids) == 0:
    print("No vector IDs found. Check your index name and namespace.")
    exit()

# Fetch vectors in batches
batch_size = 100
all_records = []

for i in range(0, len(all_ids), batch_size):
    batch_ids = all_ids[i:i+batch_size]
    try:
        batch_records = index.fetch(ids=batch_ids, namespace=namespace)
        
        # Debug information
        print(f"Batch {i//batch_size + 1}: Fetched {len(batch_records.vectors)} records")
        
        # Access the vectors from the FetchResponse object correctly
        for vector_id, vector_data in batch_records.vectors.items():
            record = {
                'id': vector_id,
            }
            
            # Add values if available
            if hasattr(vector_data, 'values'):
                record['values'] = vector_data.values
                
            # Add metadata if available
            if hasattr(vector_data, 'metadata') and vector_data.metadata:
                for key, value in vector_data.metadata.items():
                    record[f'metadata_{key}'] = value
                    
            all_records.append(record)
    except Exception as e:
        print(f"Error fetching batch {i//batch_size + 1}: {e}")

print(f"Total records processed: {len(all_records)}")

if len(all_records) == 0:
    print("No records were retrieved. Check your Pinecone index configuration.")
    exit()

# Convert the fetched records to a pandas DataFrame
df = pd.DataFrame(all_records)

# Save the DataFrame to a CSV file
output_file = 'pinecone_records.csv'
df.to_csv(output_file, index=False)
print(f"Data saved to {output_file}")

