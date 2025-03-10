import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
from pinecone import Pinecone
from sklearn.preprocessing import MinMaxScaler
import umap

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
batch_size = 1000
all_records = []
all_vectors = []
vector_ids = []

for i in range(0, len(all_ids), batch_size):
    batch_ids = all_ids[i:i+batch_size]
    try:
        batch_records = index.fetch(ids=batch_ids, namespace=namespace)
        
        # Debug information
        print(f"Batch {i//batch_size + 1}: Fetched {len(batch_records.vectors)} records")
        
        # Access the vectors from the FetchResponse object correctly
        for vector_id, vector_data in batch_records.vectors.items():
            # Skip if no values available
            if not hasattr(vector_data, 'values') or vector_data.values is None:
                print(f"Warning: Vector {vector_id} has no values, skipping")
                continue
                
            # Store the vector for dimensionality reduction
            all_vectors.append(vector_data.values)
            vector_ids.append(vector_id)
            
            # Create record with id and metadata
            record = {
                'id': vector_id,
            }
                
            # Add metadata as additional columns if available
            if hasattr(vector_data, 'metadata') and vector_data.metadata:
                for key, value in vector_data.metadata.items():
                    # Avoid overwriting id, x, or y
                    if key not in ['id', 'x', 'y']:
                        record[key] = value
                    
            all_records.append(record)
    except Exception as e:
        print(f"Error fetching batch {i//batch_size + 1}: {e}")

print(f"Total records processed: {len(all_records)}")

if len(all_records) == 0:
    print("No records were retrieved. Check your Pinecone index configuration.")
    exit()

# Convert records to DataFrame
df = pd.DataFrame(all_records)

# Perform dimensionality reduction if we have vectors
if all_vectors:
    print("Performing dimensionality reduction with UMAP...")
    try:
        # Convert vectors to numpy array
        vectors_array = np.array(all_vectors)
        
        # Check if we have enough samples for UMAP
        if len(vectors_array) >= 5:  # UMAP needs at least a few samples
            # Use UMAP for dimensionality reduction to 2D
            reducer = umap.UMAP(n_components=2, random_state=42)
            embedding = reducer.fit_transform(vectors_array)
            
            # Scale the embedding to [0,1] range
            scaler = MinMaxScaler()
            embedding_scaled = scaler.fit_transform(embedding)
            
            # Add the coordinates to the DataFrame
            for i, vector_id in enumerate(vector_ids):
                idx = df[df['id'] == vector_id].index
                if len(idx) > 0:
                    df.loc[idx[0], 'x'] = embedding_scaled[i, 0]
                    df.loc[idx[0], 'y'] = embedding_scaled[i, 1]
        else:
            print("Not enough vectors for UMAP. Using simple 2D projection.")
            # For very small datasets, just use the first 2 dimensions
            for i, vector_id in enumerate(vector_ids):
                idx = df[df['id'] == vector_id].index
                if len(idx) > 0 and len(all_vectors[i]) >= 2:
                    # Scale to [0,1]
                    x = (all_vectors[i][0] - min(v[0] for v in all_vectors)) / (max(v[0] for v in all_vectors) - min(v[0] for v in all_vectors) + 1e-10)
                    y = (all_vectors[i][1] - min(v[1] for v in all_vectors)) / (max(v[1] for v in all_vectors) - min(v[1] for v in all_vectors) + 1e-10)
                    df.loc[idx[0], 'x'] = x
                    df.loc[idx[0], 'y'] = y
    except Exception as e:
        print(f"Error during dimensionality reduction: {e}")
        print("Falling back to simple 2D projection.")
        # Fallback to using first 2 dimensions
        for i, vector_id in enumerate(vector_ids):
            idx = df[df['id'] == vector_id].index
            if len(idx) > 0 and len(all_vectors[i]) >= 2:
                df.loc[idx[0], 'x'] = all_vectors[i][0]
                df.loc[idx[0], 'y'] = all_vectors[i][1]

# Ensure the DataFrame has the required columns for Cosmograph embedding mode
required_columns = ['id', 'x', 'y']
for col in required_columns:
    if col not in df.columns:
        print(f"Warning: Required column '{col}' not found. Adding empty column.")
        df[col] = 0 if col != 'id' else 'unknown'

# Reorder columns to put id, x, y first
column_order = required_columns + [col for col in df.columns if col not in required_columns]
df = df[column_order]

# Save the DataFrame to a CSV file with semicolon separator
output_file = 'pinecone_embedding.csv'
df.to_csv(output_file, index=False, sep=';')
print(f"Data saved to {output_file} in Cosmograph embedding format")

