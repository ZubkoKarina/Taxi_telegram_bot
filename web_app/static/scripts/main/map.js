let userCityCoordinates = null;
let userCityId = null
let map;
let markers = [];
let geocoder;
let directionsService;
let directionsRenderer;

getUserCity().then(city => {
    userCity = city;

    fetch('/get_place', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({query: city}),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        userCityCoordinates = {
            lat: data.geo.lat,
            lng: data.geo.lng,
        };
        userCityId = data.id;
        initMap();
    })
    .catch(error => {
        console.error('Error:', error);
    });
});



function initMap() {
    if (!userCityCoordinates) {
        console.error("User city coordinates are not set.");
        return;
    }

    const telegramTheme = tg.colorScheme;

    const lightMapId = 'a9689db6e76bfab8';
    const darkMapId = 'f5690bdfcc14e2c3';

    const isDarkMode = telegramTheme === 'dark';
    const mapId = isDarkMode ? darkMapId : lightMapId;

    const mapOptions = {
        center: new google.maps.LatLng(userCityCoordinates.lat, userCityCoordinates.lng),
        zoom: 12,
        mapId: mapId,
        disableDefaultUI: true,
    };
    map = new google.maps.Map(document.getElementById('map'), mapOptions);
    geocoder = new google.maps.Geocoder();
    directionsService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer({
        map: map,
        suppressMarkers: true,
        polylineOptions: {
            strokeColor: '#00EDC5',
            strokeOpacity: 1,
            strokeWeight: 3
        }
    });
}

function geocodeAddress(placeId, isDestination, callback) {
    fetch('/get_place_geo', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({place_id: placeId}),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        const location = data;
        callback(location);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function calculatePriceOrder(distance, duration) {
    const taxiClassBlockActive = document.querySelector('.block-taxi-class.selected');
    console.log(taxiClassBlockActive)
    taxiClass = taxiClassBlockActive.dataset.id

    fetch(`/get-order-price?distance=${distance}&taxi_class=${taxiClass}&duration=${duration}`)
        .then(response => response.json())
        .then(data => {
            if (data) {
                const outputCost = document.getElementById('output-cost');


                outputCost.dataset.costRoad = data;
                if (!outputCost.dataset.costServices) {
                    outputCost.value = outputCost.dataset.costRoad;
                } else {
                    outputCost.value = parseFloat(outputCost.dataset.costRoad) + parseFloat(outputCost.dataset.costServices);
                }

                document.getElementById('output-cost').textContent = `${document.getElementById('output-cost').value} ₴`;
                document.getElementById('output-km').textContent = Math.round(distance / 1000) + 'км.'
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function calculateAndDisplayRoute() {
    const fromLat = parseFloat(document.getElementById('from_lat').value);
    const fromLng = parseFloat(document.getElementById('from_lng').value);
    const toLat = parseFloat(document.getElementById('to_lat').value);
    const toLng = parseFloat(document.getElementById('to_lng').value);
    const centerMarkerDiv = document.getElementById('main_marker');
    if (centerMarkerDiv) {
        centerMarkerDiv.remove()
    }

    if (isNaN(fromLat) || isNaN(fromLng) || isNaN(toLat) || isNaN(toLng)) {
        alert("Please ensure both origin and destination addresses are set correctly.");
        return;
    }

    const start = new google.maps.LatLng(fromLat, fromLng);
    const end = new google.maps.LatLng(toLat, toLng);

    const request = {
        origin: start,
        destination: end,
        travelMode: 'DRIVING'
    };

    directionsService.route(request, function(result, status) {
        if (status === 'OK') {
            console.log(result);
            directionsRenderer.setDirections(result);

            const route = result.routes[0];
            const leg = route.legs[0];

            const distance = leg.distance.value;
            const duration = leg.duration.value;

            // Створення маркерів для початкової і кінцевої точок
            const fromMarker = new google.maps.Marker({
                position: leg.start_location,
                map: map,
                icon: '../static/images/from-marker.svg'
            });
            const toMarker = new google.maps.Marker({
                position: leg.end_location,
                map: map,
                icon: '../static/images/to-marker.svg'
            });

            // Додавання маркерів у масив
            markers.push(fromMarker, toMarker);

            console.log('Відстань:', distance);
            console.log('Час подорожі:', duration);

            calculatePriceOrder(distance, duration);
        } else {
            alert('Directions request failed due to ' + status);
        }
    });
}

window.addEventListener('load', requestUserLocation);


