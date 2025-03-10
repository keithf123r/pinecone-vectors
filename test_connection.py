import os
import pinecone
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get credentials from environment variables
api_key = os.environ.get('PINECONE_API_KEY')
env = os.environ.get('PINECONE_ENVIRONMENT')

print(f"API Key exists: {bool(api_key)}")
print(f"Environment: {env}")

try:
    # Initialize Pinecone
    print("Initializing Pinecone...")
    pinecone.init(api_key=api_key, environment=env)
    
    # List available indexes
    print("Available indexes:")
    indexes = pinecone.list_indexes()
    print(indexes)
    
    if not indexes:
        print("No indexes found. Please check your Pinecone account to ensure you have created indexes.")
    
except Exception as e:
    print(f"Error: {str(e)}")
    print("Please check your Pinecone credentials and try again.") 