# 3D Vector Embeddings Visualization

This web application provides an interactive 3D visualization of your Pinecone vector embeddings. It allows you to explore your embeddings in a three-dimensional space, helping you to understand the relationships and patterns in your data.

## Features

- **Interactive 3D Visualization**: Rotate, zoom, and pan to explore your embeddings from any angle
- **Point Customization**: Adjust point size and opacity
- **Vector Information**: Click on any point to see its details, including ID and metadata
- **Statistics**: View basic statistics about your vector embeddings
- **Responsive Design**: Works on desktop and mobile devices

## Requirements

- Python 3.8+
- Pinecone API key and index
- Required Python packages (see requirements.txt)

## Installation

1. Make sure you have all the required packages installed:

```bash
pip install -r requirements.txt
```

2. Ensure your `.env` file is set up with your Pinecone credentials:

```
PINECONE_API_KEY=your_api_key
PINECONE_INDEX=your_index_name
PINECONE_NAMESPACE=your_namespace  # Optional
```

## Usage

1. Run the Flask application:

```bash
python app.py
```

2. Open your web browser and navigate to:

```
http://127.0.0.1:5000/
```

3. The application will fetch your vector embeddings from Pinecone, perform 3D dimensionality reduction using UMAP, and display them in an interactive 3D visualization.

4. You can:
   - Rotate the view by clicking and dragging
   - Zoom in/out using the scroll wheel
   - Click on points to see their details
   - Adjust point size and opacity using the sliders
   - Reset the view to the default position

## How It Works

1. The application connects to your Pinecone index and retrieves all vector embeddings
2. It uses UMAP (Uniform Manifold Approximation and Projection) to reduce the high-dimensional vectors to 3D
3. The reduced vectors are displayed in an interactive 3D scatter plot using Plotly.js
4. The first time you run the application, it will cache the processed vectors to a CSV file for faster loading on subsequent runs

## Troubleshooting

- If you encounter errors connecting to Pinecone, check your API key and index name in the `.env` file
- If the visualization is slow, try reducing the number of vectors in your index or adjusting the point size and opacity
- If you update your Pinecone index, delete the `pinecone_embedding_3d.csv` file to force the application to fetch fresh data

## License

This project is licensed under the MIT License - see the LICENSE file for details. 