# Pinecone to CSV Exporter

This tool exports vector data from a Pinecone index to a CSV file.

## Prerequisites

- Python 3.6+
- Pinecone account with at least one index

## Setup

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/pinecone-vectors.git
   cd pinecone-vectors
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your Pinecone credentials:
   ```
   cp .env.example .env
   ```

4. Edit the `.env` file with your actual Pinecone credentials:
   ```
   PINECONE_API_KEY=your_actual_api_key
   PINECONE_ENVIRONMENT=your_actual_environment
   PINECONE_INDEX=your_actual_index_name
   ```

## Usage

Run the script to export data from your Pinecone index to a CSV file:

```
python pinecone_to_csv.py
```

The script will:
1. Connect to your Pinecone account
2. List available indexes
3. Check if your specified index exists
4. Export a sample of vector data to a CSV file

## Troubleshooting

### No indexes found

If you see "No indexes found in your Pinecone account", check the following:

1. You have created indexes in your Pinecone account
   - Log in to your Pinecone account at https://app.pinecone.io/
   - Create a new index if you don't have one

2. Your API key has access to the indexes
   - Make sure you're using the correct API key
   - Check the permissions of your API key

3. You are using the correct environment
   - The environment should match the region where your index is hosted
   - Common environments: "us-east-1-aws", "us-west1-gcp", "asia-southeast1-gcp"

### Index not found

If your specified index is not found, the script will show you a list of available indexes and allow you to select one.

### Connection issues

If you encounter connection issues, check your internet connection and firewall settings.

## Testing the Connection

You can test your connection to Pinecone using the included test script:

```
python test_connection.py
```

This will show you if your API key and environment are correct, and list the available indexes in your account. 