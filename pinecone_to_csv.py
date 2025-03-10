import os
import json
import pandas as pd
from pinecone import Pinecone
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get credentials from environment variables
api_key = os.environ.get('PINECONE_API_KEY')
env = os.environ.get('PINECONE_ENVIRONMENT')
index_name = os.environ.get('PINECONE_INDEX')

# Initialize Pinecone
pc = Pinecone(api_key=api_key)
index = pc.Index(index_name)

# Get all vector IDs
print('Fetching vector IDs...')
all_ids = []
pagination_token = None

# Using list method with pagination
while True:
    params = {'limit': 100}
    if pagination_token:
        params['pagination_token'] = pagination_token
        
    response = index.list(**params)
    
    # Extract IDs based on response format
    if hasattr(response, 'vectors'):
        all_ids.extend([v.id for v in response.vectors])
    elif hasattr(response, 'ids'):
        all_ids.extend(response.ids)
    else:
        all_ids.extend(list(response))
        
    # Check if we need to continue pagination
    if hasattr(response, 'pagination') and response.pagination.next:
        pagination_token = response.pagination.next
    else:
        break
        
print(f'Found {len(all_ids)} vector IDs')

# Fetch vectors and metadata in batches
print('Fetching vector data...')
batch_size = 100
all_records = []

for i in range(0, len(all_ids), batch_size):
    batch_ids = all_ids[i:i+batch_size]
    print(f'Fetching batch {i//batch_size + 1}/{(len(all_ids) + batch_size - 1)//batch_size}')
    
    response = index.fetch(ids=batch_ids)
    
    # Handle response format differences between Pinecone versions
    vectors = response.vectors if hasattr(response, 'vectors') else response['vectors']
        
    for id, vector_data in vectors.items():
        record = {'id': id}
        
        # Add metadata if available
        metadata = getattr(vector_data, 'metadata', None) or vector_data.get('metadata')
            
        if metadata:
            for key, value in metadata.items():
                if isinstance(value, (dict, list)):
                    record[key] = json.dumps(value)
                else:
                    record[key] = value
                    
        all_records.append(record)

# Convert to DataFrame and save
output_file = 'pinecone_records.csv'
if all_records:
    df = pd.DataFrame(all_records)
    df.to_csv(output_file, index=False)
    print(f'Saved {len(all_records)} records to {output_file}')
else:
    print('No records found or error occurred.')