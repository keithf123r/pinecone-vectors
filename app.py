import os
from flask import Flask, render_template, jsonify
import pandas as pd
import numpy as np
from pinecone import Pinecone
from sklearn.preprocessing import MinMaxScaler
import umap
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

app = Flask(__name__)

def fetch_and_process_vectors():
    """Fetch vectors from Pinecone and process them for 3D visualization"""
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
        list_generator = index.list(namespace=namespace)
        
        batch_count = 0
        for batch in list_generator:
            batch_count += 1
            batch_ids = list(batch) if not isinstance(batch, list) else batch
            print(f"Retrieved batch {batch_count} with {len(batch_ids)} IDs")
            all_ids.extend(batch_ids)
            
    except Exception as e:
        print(f"Error retrieving vector IDs: {e}")
        
    print(f"Total IDs retrieved: {len(all_ids)}")

    if len(all_ids) == 0:
        return None

    # Fetch vectors in batches
    batch_size = 100
    all_records = []
    all_vectors = []
    vector_ids = []

    for i in range(0, len(all_ids), batch_size):
        batch_ids = all_ids[i:i+batch_size]
        try:
            batch_records = index.fetch(ids=batch_ids, namespace=namespace)
            
            print(f"Batch {i//batch_size + 1}: Fetched {len(batch_records.vectors)} records")
            
            for vector_id, vector_data in batch_records.vectors.items():
                if not hasattr(vector_data, 'values') or vector_data.values is None:
                    print(f"Warning: Vector {vector_id} has no values, skipping")
                    continue
                    
                all_vectors.append(vector_data.values)
                vector_ids.append(vector_id)
                
                record = {
                    'id': vector_id,
                }
                    
                if hasattr(vector_data, 'metadata') and vector_data.metadata:
                    for key, value in vector_data.metadata.items():
                        if key not in ['id', 'x', 'y', 'z']:
                            record[key] = value
                        
                all_records.append(record)
        except Exception as e:
            print(f"Error fetching batch {i//batch_size + 1}: {e}")

    print(f"Total records processed: {len(all_records)}")

    if len(all_records) == 0:
        return None

    # Convert records to DataFrame
    df = pd.DataFrame(all_records)

    # Perform 3D dimensionality reduction
    if all_vectors:
        print("Performing 3D dimensionality reduction with UMAP...")
        try:
            vectors_array = np.array(all_vectors)
            
            if len(vectors_array) >= 5:
                # Use UMAP for dimensionality reduction to 3D
                reducer = umap.UMAP(n_components=3, random_state=42)
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
                        df.loc[idx[0], 'z'] = embedding_scaled[i, 2]
            else:
                print("Not enough vectors for UMAP. Using simple 3D projection.")
                for i, vector_id in enumerate(vector_ids):
                    idx = df[df['id'] == vector_id].index
                    if len(idx) > 0 and len(all_vectors[i]) >= 3:
                        # Scale to [0,1]
                        x = (all_vectors[i][0] - min(v[0] for v in all_vectors)) / (max(v[0] for v in all_vectors) - min(v[0] for v in all_vectors) + 1e-10)
                        y = (all_vectors[i][1] - min(v[1] for v in all_vectors)) / (max(v[1] for v in all_vectors) - min(v[1] for v in all_vectors) + 1e-10)
                        z = (all_vectors[i][2] - min(v[2] for v in all_vectors)) / (max(v[2] for v in all_vectors) - min(v[2] for v in all_vectors) + 1e-10)
                        df.loc[idx[0], 'x'] = x
                        df.loc[idx[0], 'y'] = y
                        df.loc[idx[0], 'z'] = z
        except Exception as e:
            print(f"Error during dimensionality reduction: {e}")
            print("Falling back to simple 3D projection.")
            for i, vector_id in enumerate(vector_ids):
                idx = df[df['id'] == vector_id].index
                if len(idx) > 0 and len(all_vectors[i]) >= 3:
                    df.loc[idx[0], 'x'] = all_vectors[i][0]
                    df.loc[idx[0], 'y'] = all_vectors[i][1]
                    df.loc[idx[0], 'z'] = all_vectors[i][2]

    # Ensure the DataFrame has the required columns
    required_columns = ['id', 'x', 'y', 'z']
    for col in required_columns:
        if col not in df.columns:
            print(f"Warning: Required column '{col}' not found. Adding empty column.")
            df[col] = 0 if col != 'id' else 'unknown'

    return df

@app.route('/')
def index():
    """Render the main visualization page"""
    return render_template('index.html')

@app.route('/api/vectors')
def get_vectors():
    """API endpoint to get vector data"""
    try:
        # Check if we have a cached CSV file
        if os.path.exists('pinecone_embedding_3d.csv'):
            df = pd.read_csv('pinecone_embedding_3d.csv')
        else:
            # Fetch and process vectors
            df = fetch_and_process_vectors()
            if df is not None:
                # Save to CSV for caching
                df.to_csv('pinecone_embedding_3d.csv', index=False)
            else:
                return jsonify({'error': 'No vectors found'}), 404
        
        # Handle NaN values before converting to JSON
        df = df.fillna(value=None)  # Replace NaN with None (becomes null in JSON)
        
        # Convert to list of dictionaries for JSON response
        vectors_data = df.to_dict(orient='records')
        return jsonify(vectors_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 