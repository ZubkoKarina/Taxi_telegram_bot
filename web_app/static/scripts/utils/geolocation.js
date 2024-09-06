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
    const lat = position.coords.latitude;
    const lng = position.coords.longitude;
    document.getElementById('from_lat').value = lat;
    document.getElementById('from_lng').value = lng;

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
        searchInputElement = document.getElementById('from')
        searchInputElement.value = place.address;
        searchInputElement.dataset.id = place.id
        searchInputElement.dataset.address = place.address
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
