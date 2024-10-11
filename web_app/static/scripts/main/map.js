let userCityCoordinates = null;
let userCityId = null
let userRegionId = null
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
        userRegionId = data.region_id;
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
//    const mapId = 'a9689db6e76bfab8'

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
            strokeColor: '#EB8D00',
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

function calculatePriceOrder(feed_distance, trip_distance, distance_from_end_point_to_point) {
    const taxiClassBlockActive = document.querySelector('.block-taxi-class.selected');
    const taxiClass = taxiClassBlockActive.dataset.id;

    const requestBody = {
        feed_distance: feed_distance,
        trip_distance: trip_distance,
        distance_from_end_point_to_point: distance_from_end_point_to_point,
        number_idle_minutes: { "0": 0, "1": 0, "2": 0 },
        car_type_id: parseInt(taxiClass),
        is_intercity: false
    };
    console.log(requestBody)

    fetch('https://taxiuniversal.com.ua/api/order/cost_calculation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
    })
        .then(response => response.json())
        .then(data => {
            if (data) {
                const outputCost = document.getElementById('output-cost');
                outputCost.dataset.costRoad = data.data.cost;
                console.log(data.variable)
                outputCost.dataset.variable = JSON.stringify(data.variable);
                if (!outputCost.dataset.costServices) {
                    outputCost.value = outputCost.dataset.costRoad;
                } else {
                    outputCost.value = parseFloat(outputCost.dataset.costRoad) + parseFloat(outputCost.dataset.costServices);
                }

                document.getElementById('output-cost-text').textContent = `${outputCost.value} ₴`;
                document.getElementById('output-cost-text').classList.add('visible');
//                document.getElementById('output-km').textContent = Math.round(trip_distance["0"] / 1000) + ' км.';  // Беремо першу відстань для відображення
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}


function routeConstruction() {
    if (markers.length < 2) {
        alert("Необхідно принаймні дві точки для побудови маршруту.");
        return;
    }

    const origin = markers[0].getPosition();
    const destination = markers[1].getPosition();

    const waypoints = markers.slice(2).map(marker => ({
        location: marker.getPosition(),
        stopover: true
    }));

    directionsService.route(
        {
            origin: origin,
            destination: destination,
            waypoints: waypoints,
            optimizeWaypoints: false,
            travelMode: google.maps.TravelMode.DRIVING
        },
        (response, status) => {
            if (status === google.maps.DirectionsStatus.OK) {
                directionsRenderer.setDirections(response);

                let tripDistance = {};
                const legs = response.routes[0].legs;

                legs.forEach((leg, index) => {
                    tripDistance[index] = leg.distance.value / 1000;
                });

                const compareLatLng = new google.maps.LatLng(49.65202915025116, 30.97800902799662);

                computeDistanceAlongRoad(origin, compareLatLng, (feedDistance) => {
                    computeDistanceAlongRoad(compareLatLng, destination, (distance_from_end_point_to_point) => {
                        calculatePriceOrder(feedDistance, tripDistance, distance_from_end_point_to_point);
                    });
                });

            } else {
                window.alert("Не вдалося побудувати маршрут: " + status);
            }
        }
    );
}

function computeDistanceAlongRoad(pointA, pointB, callback) {
    const service = new google.maps.DirectionsService();

    service.route(
        {
            origin: pointA,
            destination: pointB,
            travelMode: google.maps.TravelMode.DRIVING
        },
        (response, status) => {
            if (status === google.maps.DirectionsStatus.OK) {
                const route = response.routes[0];
                const distance = route.legs.reduce((total, leg) => total + leg.distance.value, 0) / 1000;
                callback(distance);
            } else {
                console.error('Запит маршруту не вдався через ' + status);
                callback(null);
            }
        }
    );
}



window.addEventListener('load', requestUserLocation);


