const geoButton = document.getElementById('geo-location-button');
let markerUserGeo = null

function requestUserLocation() {
    if ("geolocation" in navigator) {
        console.log(navigator)
        navigator.geolocation.getCurrentPosition(showPosition, showError, { timeout: 4000 });
    } else {
        showNotification("Для отримання вашого місцезнаходження, увімкніть геопозицію на телефоні");
    }
}
geoButton.addEventListener("click", requestUserLocation);


function showPosition(position) {
    clearAddress()
    isListenMoveMap = true
    const lat = position.coords.latitude;
    const lng = position.coords.longitude;
    let searchFromElement = document.getElementById('from')
    searchFromElement.dataset.geo = JSON.stringify([lat, lng])
    currentInputId = 'from'

    markerUserGeo = new google.maps.Marker({
        position: new google.maps.LatLng(position.coords.latitude, position.coords.longitude),
        map: map,
        icon: {
            url: '../static/images/user-geo.svg',
            scaledSize: new google.maps.Size(60, 60)
        },
    });

    renderDriversInMap([lat, lng])

    const data = ({
        lat: lat,
        lng: lng
    });

    fetch('/get_place_by_geo', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(data => {
        place = data
        searchFromElement.value = place.address;
        searchFromElement.dataset.id = place.id
        searchFromElement.dataset.address = place.address
        MoveMarker(false)
    });

}

function showError(error) {
    switch (error.code) {
        case error.POSITION_UNAVAILABLE:
            showNotification("Інформація про місцеперебування недоступна.");
            break;
        case error.TIMEOUT:
            showNotification("Не вдалось отримати інформацію про  ваше місцеперебування. Для його отримання, увімкніть геопозицію на телефоні");
            break;
        case error.UNKNOWN_ERROR:
            showNotification("Сталася невідома помилка.");
            break;
    }
}
