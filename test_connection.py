import os
from pinecone.grpc import PineconeGRPC as Pinecone
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get credentials from environment variables
pc = Pinecone(api_key=os.environ.get('PINECONE_API_KEY'))

index_list = pc.list_indexes()

print(index_list)