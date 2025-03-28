// Global variables
let plotlyPlot = null;
let vectorData = [];
let filteredData = [];
let selectedPoint = null;
let metadataFields = [];
let activeFilters = {};

// DOM elements
const visualizationContainer = document.getElementById('visualization');
const pointSizeSlider = document.getElementById('point-size');
const opacitySlider = document.getElementById('opacity');
const resetViewButton = document.getElementById('reset-view');
const vectorInfoDiv = document.getElementById('vector-info');
const statsDiv = document.getElementById('stats');
const filtersContainer = document.getElementById('filters-container');
const applyFiltersButton = document.getElementById('apply-filters');
const resetFiltersButton = document.getElementById('reset-filters');

// Initialize the visualization
document.addEventListener('DOMContentLoaded', function() {
    // Fetch vector data from the API
    fetchVectorData();
    
    // Set up event listeners
    pointSizeSlider.addEventListener('input', updatePointSize);
    opacitySlider.addEventListener('input', updateOpacity);
    resetViewButton.addEventListener('click', resetView);
    applyFiltersButton.addEventListener('click', applyFilters);
    resetFiltersButton.addEventListener('click', resetFilters);
    
    // Add window resize handler for responsive behavior
    window.addEventListener('resize', function() {
        if (plotlyPlot) {
            Plotly.Plots.resize(plotlyPlot);
        }
    });
    
    // Dark mode toggle functionality
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const darkModeIcon = darkModeToggle.querySelector('i');
    
    // Initialize icon based on current mode
    if (document.body.classList.contains('dark-mode')) {
        darkModeIcon.classList.remove('fa-moon');
        darkModeIcon.classList.add('fa-sun');
    }
    
    darkModeToggle.addEventListener('click', function() {
        // Toggle dark mode class on document body
        document.body.classList.toggle('dark-mode');
        
        // Toggle icon between moon and sun
        darkModeIcon.classList.toggle('fa-moon');
        darkModeIcon.classList.toggle('fa-sun');
        
        // Save preference to localStorage
        const isDarkMode = document.body.classList.contains('dark-mode');
        localStorage.setItem('darkMode', isDarkMode);
        
        // Update the plot layout for dark mode if visualization exists
        if (plotlyPlot) {
            const newLayout = {
                paper_bgcolor: isDarkMode ? '#333' : '#fff',
                plot_bgcolor: isDarkMode ? '#333' : '#fff',
                font: {
                    color: isDarkMode ? '#f5f5f5' : '#333'
                }
            };
            Plotly.relayout(plotlyPlot, newLayout);
        }
    });
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
            filteredData = [...vectorData]; // Create a copy for filtering
            
            // Extract metadata fields for filters
            extractMetadataFields();
            
            // Create filters UI
            createFiltersUI();
            
            // Create visualization with all data
            createVisualization(filteredData);
            updateStats(filteredData);
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

// Extract metadata fields from vector data
function extractMetadataFields() {
    // Get all unique keys from the data
    const allKeys = new Set();
    vectorData.forEach(vector => {
        Object.keys(vector).forEach(key => {
            if (!['id', 'x', 'y', 'z'].includes(key)) {
                allKeys.add(key);
            }
        });
    });
    
    metadataFields = Array.from(allKeys);
    
    // Initialize active filters
    metadataFields.forEach(field => {
        activeFilters[field] = [];
    });
}

// Create filters UI based on metadata fields
function createFiltersUI() {
    if (metadataFields.length === 0) {
        filtersContainer.innerHTML = '<p>No metadata fields available for filtering</p>';
        return;
    }
    
    let filtersHTML = '';
    
    // Create filter groups for each metadata field
    metadataFields.forEach(field => {
        // Get unique values for this field
        const values = new Set();
        vectorData.forEach(vector => {
            if (vector[field] !== undefined && vector[field] !== null) {
                values.add(String(vector[field]));
            }
        });
        
        const uniqueValues = Array.from(values).sort();
        
        // Only create filter if there are values and not too many
        if (uniqueValues.length > 0 && uniqueValues.length <= 50) {
            filtersHTML += `
                <div class="filter-group">
                    <label class="filter-label">${field}</label>
                    <input type="text" class="filter-search" placeholder="Search ${field}..." 
                           onkeyup="filterOptions('${field}', this.value)">
                    <div class="filter-options" id="filter-options-${field}">
            `;
            
            uniqueValues.forEach(value => {
                filtersHTML += `
                    <div class="filter-checkbox">
                        <input type="checkbox" id="${field}-${value}" name="${field}" value="${value}">
                        <label for="${field}-${value}">${value}</label>
                    </div>
                `;
            });
            
            filtersHTML += `
                    </div>
                </div>
            `;
        }
    });
    
    if (filtersHTML) {
        filtersContainer.innerHTML = filtersHTML;
    } else {
        filtersContainer.innerHTML = '<p>No suitable fields for filtering</p>';
    }
}

// Filter options in a filter group
function filterOptions(field, searchText) {
    const optionsContainer = document.getElementById(`filter-options-${field}`);
    const options = optionsContainer.querySelectorAll('.filter-checkbox');
    
    searchText = searchText.toLowerCase();
    
    options.forEach(option => {
        const label = option.querySelector('label').textContent.toLowerCase();
        if (label.includes(searchText)) {
            option.style.display = '';
        } else {
            option.style.display = 'none';
        }
    });
}

// Make filterOptions globally accessible
window.filterOptions = filterOptions;

// Apply filters to the data
function applyFilters() {
    // Collect active filters
    metadataFields.forEach(field => {
        const checkboxes = document.querySelectorAll(`input[name="${field}"]:checked`);
        activeFilters[field] = Array.from(checkboxes).map(cb => cb.value);
    });
    
    // Filter the data
    filteredData = vectorData.filter(vector => {
        // Check if vector passes all active filters
        return Object.entries(activeFilters).every(([field, values]) => {
            // If no values selected for this field, pass all vectors
            if (values.length === 0) return true;
            
            // Check if vector's field value is in the selected values
            return values.includes(String(vector[field]));
        });
    });
    
    // Update visualization with filtered data
    createVisualization(filteredData);
    updateStats(filteredData);
}

// Reset all filters
function resetFilters() {
    // Uncheck all checkboxes
    document.querySelectorAll('.filter-checkbox input[type="checkbox"]').forEach(cb => {
        cb.checked = false;
    });
    
    // Clear active filters
    metadataFields.forEach(field => {
        activeFilters[field] = [];
    });
    
    // Reset to all data
    filteredData = [...vectorData];
    
    // Update visualization
    createVisualization(filteredData);
    updateStats(filteredData);
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
        // Use the header field as label if it exists, otherwise use ID
        return d.header ? `Header: ${d.header}` : `ID: ${d.id}`;
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
    
    // Check if dark mode is active
    const isDarkMode = document.body.classList.contains('dark-mode');
    
    // Layout configuration
    const layout = {
        margin: { l: 0, r: 0, b: 0, t: 0 },
        paper_bgcolor: isDarkMode ? '#333' : '#fff',
        plot_bgcolor: isDarkMode ? '#333' : '#fff',
        font: {
            color: isDarkMode ? '#f5f5f5' : '#333'
        },
        scene: {
            xaxis: { title: 'X' },
            yaxis: { title: 'Y' },
            zaxis: { title: 'Z' },
            camera: {
                eye: { x: 1.5, y: 1.5, z: 1.5 }
            }
        },
        hovermode: 'closest',
        autosize: true
    };
    
    // Plot options
    const config = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
        scrollZoom: true,
        modeBarButtonsToRemove: [
            'lasso2d', 'select2d', 'autoScale2d', 'hoverClosestCartesian',
            'hoverCompareCartesian', 'toggleSpikelines'
        ]
    };
    
    // Create or update the plot
    if (!plotlyPlot) {
        Plotly.newPlot(visualizationContainer, [trace], layout, config);
        plotlyPlot = visualizationContainer;
        
        // Add click event for vector selection
        plotlyPlot.on('plotly_click', function(data) {
            const point = data.points[0];
            const index = point.customdata;
            selectedPoint = filteredData[index];
            displayVectorInfo(selectedPoint);
        });
    } else {
        Plotly.react(plotlyPlot, [trace], layout, config);
    }
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
    
    // Start with header if available, otherwise ID
    let html = vector.header 
        ? `<p><strong>Header:</strong> ${vector.header}</p><p><strong>ID:</strong> ${vector.id}</p>`
        : `<p><strong>ID:</strong> ${vector.id}</p>`;
    
    // Add all metadata fields
    Object.keys(vector).forEach(key => {
        if (!['id', 'x', 'y', 'z', 'header'].includes(key)) {
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
    const totalOriginal = vectorData.length;
    
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
        <p><strong>Vectors Shown:</strong> ${totalVectors} of ${totalOriginal}</p>
        <p><strong>X Mean:</strong> ${xMean.toFixed(4)} (±${xStd.toFixed(4)})</p>
        <p><strong>Y Mean:</strong> ${yMean.toFixed(4)} (±${yStd.toFixed(4)})</p>
        <p><strong>Z Mean:</strong> ${zMean.toFixed(4)} (±${zStd.toFixed(4)})</p>
    `;
}

// Helper function to calculate mean
function mean(values) {
    if (values.length === 0) return 0;
    return values.reduce((sum, value) => sum + value, 0) / values.length;
}

// Helper function to calculate standard deviation
function standardDeviation(values) {
    if (values.length === 0) return 0;
    const avg = mean(values);
    const squareDiffs = values.map(value => Math.pow(value - avg, 2));
    const avgSquareDiff = mean(squareDiffs);
    return Math.sqrt(avgSquareDiff);
} 