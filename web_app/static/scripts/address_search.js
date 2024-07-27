const addressModal = document.getElementById("addressModal");
const searchInput = document.getElementById("searchInput");
const suggestions = document.getElementById("suggestions");
let currentInputId = '';
let userCity = '';
let userCityCoordinates = null;

function requestUserLocation() {
    if ("geolocation" in navigator) {
        console.log(navigator)
        navigator.geolocation.getCurrentPosition(showPosition, showError, { timeout: 5000 });
    } else {
        alert("Для отримання вашого місцезнаходження, увімкніть геопозицію на телефоні");
    }
}

function showPosition(position) {
    const lat = position.coords.latitude;
    const lng = position.coords.longitude;
    document.getElementById('from_lat').value = lat;
    document.getElementById('from_lng').value = lng;
    const latlng = new google.maps.LatLng(lat, lng);

    const geocoder = new google.maps.Geocoder();
    geocoder.geocode({ 'location': latlng }, function(results, status) {
        if (status === 'OK') {
            if (results[0]) {
                document.getElementById('from').value = results[0].formatted_address;
                placeMarker(latlng, false);
            } else {
                alert('No results found');
            }
        } else {
            alert('Geocoder failed due to: ' + status);
        }
    });
}

function showError(error) {
    switch (error.code) {
        case error.POSITION_UNAVAILABLE:
            alert("Інформація про місцезнаходження недоступна.");
            break;
        case error.TIMEOUT:
            alert("Не вадось отримати інформацю про  ваше місцезнаходження. Для його отримання, увімкніть геопозицію на телефоні");
            break;
        case error.UNKNOWN_ERROR:
            alert("Сталася невідома помилка.");
            break;
    }
}

window.addEventListener('load', requestUserLocation);

function openAddressModal(inputId) {
    currentInputId = inputId;
    addressModal.style.display = "block";
    searchInput.value = '';
    suggestions.innerHTML = '';
    searchInput.focus();
}

var FromInputElement = document.getElementById('from');
var ToInputElement = document.getElementById('to');

if (FromInputElement) {
    FromInputElement.addEventListener('click', (e) => {
        openAddressModal(e.target.id);
    });
}
if (ToInputElement) {
    ToInputElement.addEventListener('click', (e) => {
        openAddressModal(e.target.id);
    });
}

document.querySelector('.close').onclick = function() {
    addressModal.style.display = "none";
}

window.onclick = function(event) {
    if (event.target == addressModal) {
        addressModal.style.display = "none";
    }
}

function getUserCity() {
    console.log(tg.initDataUnsafe)
    const chat_id = tg.initDataUnsafe.user.id
    return fetch(`/get-user-city?chat_id=${chat_id}`)
        .then(response => response.text())
        .catch(error => {
            console.error('Error:', error);
            return null;
        });
}

function geocodeCity(city, callback) {
    const geocoder = new google.maps.Geocoder();
    geocoder.geocode({ 'address': city }, function(results, status) {
        if (status === 'OK') {
            const location = results[0].geometry.location;
            console.log(`Geocoded City: ${city}, Location: ${location.lat()}, ${location.lng()}`);
            callback(location);
        } else {
            alert('Geocode was not successful for the following reason: ' + status);
        }
    });
}

getUserCity().then(city => {
    userCity = city;
    console.log(`User City stored in variable: ${userCity}`);
    geocodeCity(userCity, function(location) {
        userCityCoordinates = {
            lat: location.lat(),
            lng: location.lng()
        };
        console.log(`User City Coordinates: ${JSON.stringify(userCityCoordinates)}`);
    });
});

searchInput.addEventListener('input', function() {
    const query = this.value;
    if (query.length > 2 && userCityCoordinates) {
        console.log(`Searching for: ${query}, Near: ${userCity}`);
        const service = new google.maps.places.AutocompleteService();

        // Перший пошук: query + userCity
        const combinedQuery = `${query}, ${userCity}`;
        service.getPlacePredictions({
            input: combinedQuery,
            componentRestrictions: { country: 'UA' },
            locationBias: new google.maps.Circle({
                center: new google.maps.LatLng(userCityCoordinates.lat, userCityCoordinates.lng),
                radius: 30000
            }),
            language: 'uk',
        }, (combinedPredictions, combinedStatus) => {
            if (combinedStatus !== google.maps.places.PlacesServiceStatus.OK || !combinedPredictions) {
                console.log(`Autocomplete failed 1: ${combinedStatus}`);
            }

            // Другий пошук: просто query
            service.getPlacePredictions({
                input: query,
                componentRestrictions: { country: 'UA' },
                locationBias: new google.maps.Circle({
                    center: new google.maps.LatLng(userCityCoordinates.lat, userCityCoordinates.lng),
                    radius: 30000
                }),
                language: 'uk',
            }, (predictions, status) => {
                if (status !== google.maps.places.PlacesServiceStatus.OK || !predictions) {
                    console.log(`Autocomplete failed 2: ${status}`);
                }

                suggestions.innerHTML = '';
                let specificAddressResults = [];
                let uniqueAddresses = new Set();
                let allPredictions = [];

                if (predictions) {
                    allPredictions = predictions;
                }
                if (combinedPredictions) {
                    allPredictions = combinedPredictions;
                }
                if (predictions && combinedPredictions) {
                    allPredictions = combinedPredictions.concat(predictions);
                }

                allPredictions.forEach((prediction) => {
                    const address = prediction.description.toLowerCase();
                    if (!uniqueAddresses.has(address)) {
                        uniqueAddresses.add(address);
                        specificAddressResults.push(prediction);
                    }
                });

                specificAddressResults.forEach((prediction) => {
                    const li = document.createElement('li');
                    li.innerHTML = `<strong>${prediction.terms[0].value} ${prediction.terms[1].value}</strong><br><small>${prediction.terms[2].value}</small>`;
                    li.onclick = () => {
                        document.getElementById(currentInputId).value = prediction.description;
                        addressModal.style.display = "none";
                        handleAddressSelection(prediction.description, currentInputId === 'to');
                    };
                    suggestions.appendChild(li);
                });
            });
        });
    } else {
        suggestions.innerHTML = '';
    }
});


function handleAddressSelection(address, isDestination) {
    geocodeAddress(address, isDestination, (location) => {
        document.getElementById(currentInputId + '_lat').value = location.lat();
        document.getElementById(currentInputId + '_lng').value = location.lng();
        placeMarker(location, isDestination);
        if (isDestination) {
            calculateAndDisplayRoute();
        }
    });
}

