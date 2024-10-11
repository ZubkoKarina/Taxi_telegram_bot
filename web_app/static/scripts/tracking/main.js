let driver_chat_id = null;
let start_point_geo = null;
let tg = window.Telegram.WebApp;
tg.expand();
const chat_id = tg.initDataUnsafe.user.id;
let directionsService;
let directionsRenderer;
let map, driverMarker;
let driverLocation = null;
let currentRoute = null;

async function getOrderInfo(chat_id) {
    try {
        const response = await fetch(`/get-order-info?chat_id=${chat_id}`);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();

        driver_chat_id = data.driver_chat_id;
        const carName = data.car_name;
        const carNumber = data.car_number;
        start_point_geo = { lat: data.start_point_geo.lat, lng: data.start_point_geo.lng };

        document.querySelector(".car-name").textContent = carName;
        document.querySelector(".car-number").textContent = carNumber;

    } catch (error) {
        console.error('Error fetching order info:', error);
    }
}

async function getDriverLocation(driver_chat_id) {
    try {
        const response = await fetch(`/get-driver-location?chat_id=${driver_chat_id}`);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        driverLocation = data;
        console.log('Updated driverLocation:', driverLocation);
    } catch (error) {
        console.error('Error:', error);
    }
}

async function initMap() {
    await getOrderInfo(chat_id);

    const mapId = 'a9689db6e76bfab8';

    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 15,
        center: start_point_geo,
        mapId: mapId,
        disableDefaultUI: true,
    });

    await getDriverLocation(driver_chat_id);


    driverMarker = new google.maps.Marker({
        map: map,
        position: driverLocation,
        icon: {
            url: '../static/images/driver-marker.svg',
            scaledSize: new google.maps.Size(30, 30),
            anchor: new google.maps.Point(15, 15)
        },
    });

    directionsService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer({
        map: map,
        suppressMarkers: true,
        polylineOptions: {
            strokeColor: '#EB8D00',
            strokeOpacity: 1,
            strokeWeight: 5
        }
    });
    console.log(start_point_geo)
    console.log(driverLocation)
    buildRoute(driverMarker.getPosition(), start_point_geo);

    setInterval(updateDriverLocation, 10000);
}

async function updateDriverLocation() {
    await getDriverLocation(driver_chat_id);
    driverMarker.setPosition(driverLocation);
    checkDriverDeviation();
}

function buildRoute(driverLocation, endPoint) {
    console.log(driverLocation);
    const request = {
        origin: driverLocation,
        destination: endPoint,
        travelMode: google.maps.TravelMode.DRIVING
    };

    directionsService.route(request, function (result, status) {
        if (status === google.maps.DirectionsStatus.OK) {
            directionsRenderer.setDirections(result);
            currentRoute = result.routes[0].legs[0].steps.flatMap(step => step.path); // Зберігайте шлях
        }
    });
}

function checkDriverDeviation() {
    if (!currentRoute || currentRoute.length === 0) return;

    const currentPos = new google.maps.LatLng(driverLocation.lat, driverLocation.lng);

    const nearestPoint = currentRoute[0];

    const distance = google.maps.geometry.spherical.computeDistanceBetween(currentPos, nearestPoint);
    console.log(`Відстань до маршруту: ${distance} м`);

    // Перевірка на відхилення від маршруту
    if (distance > 20) {
        console.log("Водій відхилився від маршруту. Перерахунок...");
        buildRoute(driverLocation, start_point_geo);
    }
}
