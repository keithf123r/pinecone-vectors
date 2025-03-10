import os
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

# Initialize Pinecone
print("Initializing Pinecone...")
pinecone.init(api_key=api_key, environment=env)

# List available indexes
print("Available indexes:")
print(pinecone.list_indexes())

# Try to connect to the specified index
if index_name in pinecone.list_indexes():
    print(f"Connecting to index '{index_name}'...")
    index = pinecone.Index(index_name)
    print("Connection successful!")
    
    # Get index stats
    print("Index stats:")
    print(index.describe_index_stats())
else:
    print(f"Index '{index_name}' not found in available indexes.") 