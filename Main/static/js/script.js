mapboxgl.accessToken = 'pk.eyJ1IjoiYmlsbGZyYW5rIiwiYSI6ImNsczB1dHcwdjA2MDYydm1lNXU0ajhjengifQ.5txbLL0MIJR-kNICK_HL6Q'; // Replace with your Mapbox access token

var map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/light-v10', // Choose a map style, you can customize this
    center: [-8.6100, 41.1496], // Center the map on Portugal
    zoom: 6 // Adjust the zoom level as needed
});

// Add a source for Portugal states geojson data
map.on('load', function () {
    map.addSource('portugal-states', {
        type: 'geojson',
        data: '/Files/georef-portugal-distrito.geojson' // Replace with the URL to your geojson file
    });

    // Add a layer to style the states
    map.addLayer({
        id: 'portugal-states-layer',
        type: 'fill',
        source: 'portugal-states',
        paint: {
            'fill-color': '#088',
            'fill-opacity': 0.8
        }
    });
});


