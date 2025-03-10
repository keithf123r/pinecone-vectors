import os
import json
import pandas as pd
import pinecone
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get credentials from environment variables
api_key = os.environ.get('PINECONE_API_KEY')
env = os.environ.get('PINECONE_ENVIRONMENT')
index_name = os.environ.get('PINECONE_INDEX')

print(f"API Key exists: {bool(api_key)}")
print(f"Environment: {env}")
print(f"Index name: {index_name}")

try:
    # Initialize Pinecone
    print("Initializing Pinecone...")
    pinecone.init(api_key=api_key, environment=env)
    
    # List available indexes
    print("Available indexes:")
    indexes = pinecone.list_indexes()
    print(indexes)
    
    if not indexes:
        print("\nNo indexes found in your Pinecone account. Please check the following:")
        print("1. You have created indexes in your Pinecone account")
        print("2. Your API key has access to the indexes")
        print("3. You are using the correct environment")
        print("\nYou can create an index in the Pinecone console or using the Pinecone API.")
        exit(1)
    
    if index_name not in indexes:
        print(f"\nThe specified index '{index_name}' was not found in your available indexes.")
        print("Please check the index name in your .env file.")
        print(f"Available indexes: {', '.join(indexes)}")
        
        # Ask if the user wants to use one of the available indexes
        if indexes:
            print("\nWould you like to use one of the available indexes? (y/n)")
            choice = input().lower()
            if choice == 'y':
                print("\nPlease select an index by number:")
                for i, idx in enumerate(indexes):
                    print(f"{i+1}. {idx}")
                
                selection = int(input()) - 1
                if 0 <= selection < len(indexes):
                    index_name = indexes[selection]
                    print(f"\nUsing index: {index_name}")
                else:
                    print("Invalid selection. Exiting.")
                    exit(1)
            else:
                print("Exiting.")
                exit(1)
    
    # Get the index
    index = pinecone.Index(index_name)
    
    # Get index stats to understand the data
    print('\nFetching index stats...')
    stats = index.describe_index_stats()
    print(f'Total vector count: {stats.total_vector_count}')
    
    if stats.total_vector_count == 0:
        print("The index is empty. No vectors to export.")
        exit(0)
    
    # Fetch vectors and metadata
    print('\nFetching vector data...')
    all_records = []
    
    # Since there's no direct list method in v2.2.4, we'll use a query with no filter
    # to get a sample of vectors, then use their IDs to fetch the full data
    
    # First, get a sample of vector IDs using a query
    sample_size = min(100, stats.total_vector_count)
    
    # Query with no specific vector, just to get some IDs
    # We need to know the dimension of the vectors
    dimensions = stats.dimension if hasattr(stats, 'dimension') else 1536  # Default to 1536 if not available
    
    query_response = index.query(
        vector=[0] * dimensions,
        top_k=sample_size,
        include_metadata=True
    )
    
    # Extract IDs from the query response
    sample_ids = [match.id for match in query_response.matches]
    
    print(f'Found {len(sample_ids)} sample vector IDs')
    
    if sample_ids:
        # Fetch the full data for these IDs
        fetch_response = index.fetch(ids=sample_ids)
        
        # Process the fetched vectors
        for id, vector_data in fetch_response.vectors.items():
            record = {'id': id}
            
            # Add metadata if available
            if hasattr(vector_data, 'metadata') and vector_data.metadata:
                for key, value in vector_data.metadata.items():
                    if isinstance(value, (dict, list)):
                        record[key] = json.dumps(value)
                    else:
                        record[key] = value
                        
            all_records.append(record)
    
    # Convert to DataFrame and save
    output_file = 'pinecone_sample.csv'
    if all_records:
        df = pd.DataFrame(all_records)
        df.to_csv(output_file, index=False)
        print(f'\nSaved {len(all_records)} sample records to {output_file}')
        print(f'Note: This is a sample of records. The full index contains {stats.total_vector_count} vectors.')
    else:
        print('\nNo records found in the sample.')
        
except Exception as e:
    print(f'\nError: {str(e)}')
    print('Please check your Pinecone credentials and index configuration.')