// Global variables
let plotlyPlot = null;
let vectorData = [];
let selectedPoint = null;

// DOM elements
const visualizationContainer = document.getElementById('visualization');
const pointSizeSlider = document.getElementById('point-size');
const opacitySlider = document.getElementById('opacity');
const resetViewButton = document.getElementById('reset-view');
const vectorInfoDiv = document.getElementById('vector-info');
const statsDiv = document.getElementById('stats');

// Initialize the visualization
document.addEventListener('DOMContentLoaded', function() {
    // Fetch vector data from the API
    fetchVectorData();
    
    // Set up event listeners
    pointSizeSlider.addEventListener('input', updatePointSize);
    opacitySlider.addEventListener('input', updateOpacity);
    resetViewButton.addEventListener('click', resetView);
});

// Fetch vector data from the API
function fetchVectorData() {
    fetch('/api/vectors')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            vectorData = data;
            createVisualization(vectorData);
            updateStats(vectorData);
        })
        .catch(error => {
            console.error('Error fetching vector data:', error);
            visualizationContainer.innerHTML = `
                <div class="alert alert-danger" role="alert">
                    Error loading vector data: ${error.message}
                </div>
            `;
        });
}

// Create the 3D visualization
function createVisualization(data) {
    // Extract coordinates
    const x = data.map(d => d.x);
    const y = data.map(d => d.y);
    const z = data.map(d => d.z);
    const ids = data.map(d => d.id);
    
    // Create hover text
    const hoverText = data.map(d => {
        // Only show the header (ID) as label
        return `ID: ${d.id}`;
    });
    
    // Create the scatter3d trace
    const trace = {
        type: 'scatter3d',
        mode: 'markers',
        x: x,
        y: y,
        z: z,
        text: hoverText,
        hoverinfo: 'text',
        marker: {
            size: parseInt(pointSizeSlider.value),
            opacity: parseFloat(opacitySlider.value),
            color: z,
            colorscale: 'Viridis',
            showscale: true,
            colorbar: {
                title: 'Z Value',
                thickness: 20,
                len: 0.5
            }
        },
        customdata: data.map((d, i) => i)  // Store index for click events
    };
    
    // Layout configuration
    const layout = {
        margin: { l: 0, r: 0, b: 0, t: 0 },
        scene: {
            xaxis: { title: 'X' },
            yaxis: { title: 'Y' },
            zaxis: { title: 'Z' },
            camera: {
                eye: { x: 1.5, y: 1.5, z: 1.5 }
            }
        },
        hovermode: 'closest'
    };
    
    // Plot options
    const config = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToRemove: [
            'lasso2d', 'select2d', 'autoScale2d', 'hoverClosestCartesian',
            'hoverCompareCartesian', 'toggleSpikelines'
        ]
    };
    
    // Create the plot
    Plotly.newPlot(visualizationContainer, [trace], layout, config);
    
    // Store the plot reference
    plotlyPlot = visualizationContainer;
    
    // Add click event listener
    visualizationContainer.on('plotly_click', function(data) {
        const point = data.points[0];
        const index = point.customdata;
        selectedPoint = vectorData[index];
        displayVectorInfo(selectedPoint);
    });
}

// Update point size
function updatePointSize() {
    const newSize = parseInt(pointSizeSlider.value);
    Plotly.restyle(plotlyPlot, 'marker.size', newSize);
}

// Update opacity
function updateOpacity() {
    const newOpacity = parseFloat(opacitySlider.value);
    Plotly.restyle(plotlyPlot, 'marker.opacity', newOpacity);
}

// Reset view
function resetView() {
    const defaultCamera = {
        eye: { x: 1.5, y: 1.5, z: 1.5 },
        center: { x: 0, y: 0, z: 0 },
        up: { x: 0, y: 0, z: 1 }
    };
    
    Plotly.relayout(plotlyPlot, {
        'scene.camera': defaultCamera
    });
}

// Display vector information
function displayVectorInfo(vector) {
    if (!vector) {
        vectorInfoDiv.innerHTML = '<p>Click on a point to see details</p>';
        return;
    }
    
    let html = `<p><strong>ID:</strong> ${vector.id}</p>`;
    
    // Add all metadata fields
    Object.keys(vector).forEach(key => {
        if (!['id', 'x', 'y', 'z'].includes(key)) {
            html += `<p><strong>${key}:</strong> ${vector[key]}</p>`;
        }
    });
    
    // Add coordinates
    html += `<p><strong>Coordinates:</strong><br>`;
    html += `X: ${vector.x.toFixed(4)}<br>`;
    html += `Y: ${vector.y.toFixed(4)}<br>`;
    html += `Z: ${vector.z.toFixed(4)}</p>`;
    
    vectorInfoDiv.innerHTML = html;
}

// Update statistics
function updateStats(data) {
    const totalVectors = data.length;
    
    // Calculate basic statistics
    const xValues = data.map(d => d.x);
    const yValues = data.map(d => d.y);
    const zValues = data.map(d => d.z);
    
    const xMean = mean(xValues);
    const yMean = mean(yValues);
    const zMean = mean(zValues);
    
    const xStd = standardDeviation(xValues);
    const yStd = standardDeviation(yValues);
    const zStd = standardDeviation(zValues);
    
    // Display statistics
    statsDiv.innerHTML = `
        <p><strong>Total Vectors:</strong> ${totalVectors}</p>
        <p><strong>X Mean:</strong> ${xMean.toFixed(4)} (±${xStd.toFixed(4)})</p>
        <p><strong>Y Mean:</strong> ${yMean.toFixed(4)} (±${yStd.toFixed(4)})</p>
        <p><strong>Z Mean:</strong> ${zMean.toFixed(4)} (±${zStd.toFixed(4)})</p>
    `;
}

// Helper function to calculate mean
function mean(values) {
    return values.reduce((sum, value) => sum + value, 0) / values.length;
}

// Helper function to calculate standard deviation
function standardDeviation(values) {
    const avg = mean(values);
    const squareDiffs = values.map(value => Math.pow(value - avg, 2));
    const avgSquareDiff = mean(squareDiffs);
    return Math.sqrt(avgSquareDiff);
} 