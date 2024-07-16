const darkModeStyle = [
    {
        "featureType": "all",
        "elementType": "geometry.fill",
        "stylers": [
            {
                "saturation": "0"
            },
            {
                "lightness": "0"
            }
        ]
    },
    {
        "featureType": "all",
        "elementType": "labels",
        "stylers": [
            {
                "visibility": "on"
            }
        ]
    },
    {
        "featureType": "all",
        "elementType": "labels.text.fill",
        "stylers": [
            {
                "saturation": 36
            },
            {
                "color": "#000000"
            },
            {
                "lightness": 40
            }
        ]
    },
    {
        "featureType": "all",
        "elementType": "labels.text.stroke",
        "stylers": [
            {
                "visibility": "on"
            },
            {
                "color": "#000000"
            },
            {
                "lightness": 16
            }
        ]
    },
    {
        "featureType": "all",
        "elementType": "labels.icon",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    },
    {
        "featureType": "administrative",
        "elementType": "geometry.fill",
        "stylers": [
            {
                "color": "#000000"
            },
            {
                "lightness": 20
            }
        ]
    },
    {
        "featureType": "administrative",
        "elementType": "geometry.stroke",
        "stylers": [
            {
                "color": "#000000"
            },
            {
                "lightness": 17
            },
            {
                "weight": 1.2
            }
        ]
    },
    {
        "featureType": "administrative.country",
        "elementType": "labels.text.fill",
        "stylers": [
            {
                "color": "#e5c163"
            }
        ]
    },
    {
        "featureType": "administrative.locality",
        "elementType": "labels.text.fill",
        "stylers": [
            {
                "color": "#c4c4c4"
            }
        ]
    },
    {
        "featureType": "administrative.neighborhood",
        "elementType": "labels.text.fill",
        "stylers": [
            {
                "color": "#e5c163"
            }
        ]
    },
    {
        "featureType": "landscape",
        "elementType": "geometry",
        "stylers": [
            {
                "color": "#000000"
            },
            {
                "lightness": 20
            }
        ]
    },
    {
        "featureType": "poi",
        "elementType": "all",
        "stylers": [
            {
                "visibility": "on"
            }
        ]
    },
    {
        "featureType": "poi",
        "elementType": "geometry",
        "stylers": [
            {
                "color": "#000000"
            },
            {
                "lightness": 21
            },
            {
                "visibility": "on"
            }
        ]
    },
    {
        "featureType": "poi.attraction",
        "elementType": "all",
        "stylers": [
            {
                "visibility": "on"
            }
        ]
    },
    {
        "featureType": "poi.attraction",
        "elementType": "geometry.fill",
        "stylers": [
            {
                "visibility": "on"
            }
        ]
    },
    {
        "featureType": "poi.business",
        "elementType": "geometry",
        "stylers": [
            {
                "visibility": "on"
            }
        ]
    },
    {
        "featureType": "poi.government",
        "elementType": "all",
        "stylers": [
            {
                "visibility": "on"
            }
        ]
    },
    {
        "featureType": "poi.park",
        "elementType": "all",
        "stylers": [
            {
                "visibility": "on"
            }
        ]
    },
    {
        "featureType": "road.highway",
        "elementType": "geometry.fill",
        "stylers": [
            {
                "color": "#eb8d00"
            },
            {
                "lightness": "0"
            }
        ]
    },
    {
        "featureType": "road.highway",
        "elementType": "geometry.stroke",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    },
    {
        "featureType": "road.highway",
        "elementType": "labels.text.stroke",
        "stylers": [
            {
                "color": "#e5c163"
            }
        ]
    },
    {
        "featureType": "road.highway",
        "elementType": "labels.icon",
        "stylers": [
            {
                "visibility": "on"
            }
        ]
    },
    {
        "featureType": "road.arterial",
        "elementType": "geometry",
        "stylers": [
            {
                "color": "#000000"
            },
            {
                "lightness": 18
            }
        ]
    },
    {
        "featureType": "road.arterial",
        "elementType": "geometry.fill",
        "stylers": [
            {
                "color": "#575757"
            }
        ]
    },
    {
        "featureType": "road.arterial",
        "elementType": "labels.text.fill",
        "stylers": [
            {
                "color": "#ffffff"
            }
        ]
    },
    {
        "featureType": "road.arterial",
        "elementType": "labels.text.stroke",
        "stylers": [
            {
                "color": "#2c2c2c"
            }
        ]
    },
    {
        "featureType": "road.local",
        "elementType": "geometry",
        "stylers": [
            {
                "color": "#000000"
            },
            {
                "lightness": 16
            }
        ]
    },
    {
        "featureType": "transit",
        "elementType": "geometry",
        "stylers": [
            {
                "color": "#000000"
            },
            {
                "lightness": 19
            }
        ]
    },
    {
        "featureType": "water",
        "elementType": "geometry",
        "stylers": [
            {
                "color": "#000000"
            },
            {
                "lightness": 17
            }
        ]
    }
];

let map;
let markers = [];
let geocoder;
let directionsService;
let directionsRenderer;

function initMap() {
    const mapOptions = {
        center: { lat: 50.4501, lng: 30.5234 },
        zoom: 18,
        styles: darkModeStyle,
        disableDefaultUI: true,
    };
    map = new google.maps.Map(document.getElementById('map'), mapOptions);
    geocoder = new google.maps.Geocoder();
    directionsService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer({
        map: map,
        suppressMarkers: true,
        polylineOptions: {
            strokeColor: 'white',
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
    orderButton.textContent = `Замовити (${0.00} грн)`;
    orderButton.value = `0.00`;
//    const taxiClass = document.getElementById('class').value;
//    fetch(`/get-order-price?distance=${distance}&taxi_class=${taxiClass}&duration=${duration}`)
//        .then(response => response.json())
//        .then(data => {
//            if (data && data.price) {
//                const orderButton = document.querySelector('.order-button');
//                orderButton.textContent = `Замовити (${data.cost} грн)`;
//            }
//        })
//        .catch(error => {
//            console.error('Error:', error);
//        });
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
