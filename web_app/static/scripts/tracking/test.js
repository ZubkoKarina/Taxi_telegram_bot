let directionsService;
let directionsRenderer;
let routePolyline;
let remainingPath = [];
let driverLocation = {lat: 0, lng: 0}
let routeIndex = 0;
let map, marker;
const rerouteThreshold = 100;  // Порогове значення для відхилення від маршруту (в метрах)

function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 12,
        center: { lat: 50.4501, lng: 30.5234 }  // Початкова позиція водія
    });

    // Маркер водія
    marker = new google.maps.Marker({
        map: map,
        position: { lat: 50.4501, lng: 30.5234 }  // Початкова позиція
    });

    // Ініціалізація сервісу та рендерера для маршруту
    directionsService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer({
        map: map,
        suppressMarkers: true  // Не показувати маркери старту та фінішу
    });

    // Прокласти початковий маршрут від водія до призначення
    calculateRoute(marker.getPosition(), { lat: 50.4591, lng: 30.5289 });

    // Імітація руху водія
    setInterval(simulateDriverMovement, 2000);  // Оновлення кожні 2 секунди
}

// Функція для розрахунку маршруту
function calculateRoute(driverLocation, destination) {
    const request = {
        origin: driverLocation,
        destination: destination,
        travelMode: google.maps.TravelMode.DRIVING
    };

    directionsService.route(request, function (result, status) {
        if (status === google.maps.DirectionsStatus.OK) {
            // Відображаємо маршрут за допомогою DirectionsRenderer
            directionsRenderer.setDirections(result);

            // Отримуємо маршрут для імітації руху
            const route = result.routes[0].legs[0].steps;
            remainingPath = route.flatMap(step => step.path);  // Масив точок для імітації руху
            routeIndex = 0;

            // Оновлюємо маршрут на мапі
            updateRouteOnMap(remainingPath);
        } else {
            console.error("Помилка розрахунку маршруту: ", status);
        }
    });
}

// Функція для імітації руху водія
function simulateDriverMovement() {
    if (remainingPath.length > 0 && routeIndex < remainingPath.length) {
        const currentPosition = remainingPath[routeIndex];
        marker.setPosition(currentPosition);
        map.setCenter(currentPosition);
        routeIndex++;

        // Оновлюємо маршрут, видаляючи вже пройдену частину
        updateRouteOnMap(remainingPath.slice(routeIndex));

        // Перевіряємо, чи не відхилився водій від маршруту
        if (hasDriverDeviated(currentPosition)) {
            console.log("Відхилення від маршруту. Перерахунок...");
            // Будуємо новий маршрут від поточної позиції водія
            calculateRoute(currentPosition, { lat: 50.4591, lng: 30.5289 });
        }
    } else {
        console.log("Маршрут завершено або залишилось недостатньо точок для руху.");
    }
}

// Функція для перевірки, чи відхилився водій від маршруту
function hasDriverDeviated(currentPosition) {
    if (remainingPath.length === 0) return false;

    const nearestPoint = remainingPath[0];  // Найближча точка маршруту
    const distance = google.maps.geometry.spherical.computeDistanceBetween(
        new google.maps.LatLng(currentPosition),
        new google.maps.LatLng(nearestPoint)
    );

    console.log(`Відстань до маршруту: ${distance} м`);

    // Якщо водій відхилився на порогову відстань, повертаємо true
    return distance > rerouteThreshold;
}

// Функція для оновлення відображеного маршруту
function updateRouteOnMap(path) {
    // Очищуємо попередній Polyline
    if (routePolyline) {
        routePolyline.setMap(null);
    }

    // Створюємо новий Polyline для відображення маршруту
    routePolyline = new google.maps.Polyline({
        path: path,
        geodesic: true,
        strokeColor: '#FF0000',
        strokeOpacity: 1.0,
        strokeWeight: 4
    });

    // Відображаємо новий Polyline
    routePolyline.setMap(map);
}
