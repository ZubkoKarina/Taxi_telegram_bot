
let map;
let markers = [];
let geocoder;
let directionsService;
let directionsRenderer;

function initMap() {
    const themeParams = tg.themeParams;
    console.log(themeParams)

    const mapOptions = {
        center: { lat: 50.4501, lng: 30.5234 },
        zoom: 18,
        styles: applyThemeToStyle(themeParams),
        disableDefaultUI: true,
    };
    map = new google.maps.Map(document.getElementById('map'), mapOptions);
    geocoder = new google.maps.Geocoder();
    directionsService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer({
        map: map,
        suppressMarkers: true,
        polylineOptions: {
            strokeColor: themeParams.text_color,
            strokeOpacity: 1,
            strokeWeight: 5
        }
    });
}

function placeMarker(location, isDestination) {
    if (isDestination) {
        directionsRenderer.setDirections({ routes: [] });

        if (markers.length === 2) {
            markers[1].setMap(null);
            markers.pop();
        }
    } else {
        markers.forEach(marker => marker.setMap(null));
        markers = [];
    }

    const marker = new google.maps.Marker({
        position: location,
        map: map,
        title: isDestination ? 'Destination' : 'Start',
        icon: {
            url: isDestination ? '../static/images/destination.svg' : '../static/images/destination.svg',
            scaledSize: new google.maps.Size(20, 20)
        }
    });

    markers.push(marker);
    map.setCenter(location);

    if (markers.length === 2) {
        calculateAndDisplayRoute();
    }
}

function geocodeAddress(address, isDestination, callback) {
    geocoder.geocode({ 'address': address }, function(results, status) {
        if (status === 'OK') {
            const location = results[0].geometry.location;
            placeMarker(location, isDestination);
            callback(location);
        } else {
            alert('Geocode was not successful for the following reason: ' + status);
        }
    });
}

function calculatePriceOrder(distance, duration) {
    const orderButton = document.querySelector('.order-button');
    const taxiClass = document.getElementById('class').value;
    fetch(`/get-order-price?distance=${distance}&taxi_class=${taxiClass}&duration=${duration}`)
        .then(response => response.json())
        .then(data => {
            if (data) {
                const orderButton = document.querySelector('.order-button');
                orderButton.textContent = `Замовити (${data} грн)`;
                orderButton.value = data;
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function calculateAndDisplayRoute() {
    const start = markers[0].getPosition();
    const end = markers[1].getPosition();

    const request = {
        origin: start,
        destination: end,
        travelMode: 'DRIVING'
    };

    directionsService.route(request, function(result, status) {
        if (status === 'OK') {
            console.log(result)
            directionsRenderer.setDirections(result);

            const route = result.routes[0];
            const leg = route.legs[0];

            const distance = leg.distance.value;
            const duration = leg.duration.value;

            console.log('Відстань:', distance);
            console.log('Час подорожі:', duration);

            calculatePriceOrder(distance, duration)
        } else {
            alert('Directions request failed due to ' + status);
        }
    });
}

document.addEventListener("DOMContentLoaded", initMap);
