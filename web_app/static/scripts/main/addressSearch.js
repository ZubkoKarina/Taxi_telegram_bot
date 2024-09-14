const searchInput = document.getElementById("address-search-input");
const suggestions = document.getElementById("suggestions");
let currentInputId = '';
let timeout = null;

searchInput.addEventListener('input', function() {
    clearTimeout(timeout);
    const pinDiv = document.getElementById('main-marker');

    if (pinDiv) {
        pinDiv.remove()
    }

    timeout = setTimeout(() => {
        let list_address = [];
        const query = this.value;
        const data = {
            city_id: userCityId,
            query: query
        };

        if (query.length < 3 && !userCityCoordinates) {
            return;
        }
        suggestions.innerHTML = '';

        fetch('/search_places', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })
        .then(response => response.json())
        .then(data => {
            list_address = data;
            list_address.forEach((address) => {
                const li = document.createElement('li');
                li.innerHTML = `${address.name}<br><small>${address.description}</small>`;
                li.onclick = () => {

                    const isStreet = address.categories === 'adr_street';
                    if (isStreet) {
                        outputAddressNumbers(address.id)
                    } else {

                        closeSearchAddressModal()
                        handleAddressSelection(address, currentInputId === 'from');
                        openSelectionAddress()

                    }
                }
                suggestions.appendChild(li);
            });
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }, 1000);
});


function outputAddressNumbers(street_id) {
    let list_address = [];
    const data = ({
        street_id: street_id,
    });

    suggestions.innerHTML = '';

    fetch('/get_address_numbers', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(data => {
        list_address = data;
        list_address.forEach((address) => {
            const li = document.createElement('li');
            li.innerHTML = `${address.name}<br><small>${address.description}</small>`;
            li.onclick = () => {
                closeSearchAddressModal()
                handleAddressSelection(address, currentInputId === 'from');
                openSelectionAddress()

            }
            suggestions.appendChild(li);
        });
    })
    .catch(error => {
        console.error('Error:', error);
    });
};

function handleAddressSelection(address, isAddressFrom) {
    const searchInputElement = document.getElementById(currentInputId);
    geocodeAddress(address.id, isAddressFrom, (location) => {
        if (currentInputId == 'from' || currentInputId == 'to') {
            searchInputElement.value = address.address;
            searchInputElement.dataset.id = address.id
            searchInputElement.dataset.address = address.address
            searchInputElement.dataset.geo = JSON.stringify([location.lat, location.lng])
        }
        if (currentInputId == 'add-stop-button') {
            let addressList = searchInputElement.dataset.addressList ? JSON.parse(searchInputElement.dataset.addressList) : [];
            addressList.push({
                address: address.address,
                id: address.id,
                geo: [location.lat, location.lng]
            });
            searchInputElement.dataset.addressList = JSON.stringify(addressList);
        }

        if (isAddressFrom) {
            map.setCenter({ lat: location.lat, lng: location.lng });
            if (markers.length != 0) {
                clearAddress()
            }
            MoveMarker(false);
        }
        map.setZoom(18)
        placeMarker(location.lat,  location.lng)
    });
}

function clearAddress() {
    const fromElement = document.getElementById('from');
    const toElement = document.getElementById('to');
    const additionalAddressElement = document.getElementById('add-stop-button');

    fromElement.value = '';
    toElement.value = '';
    if (additionalAddressElement.value) {
        additionalAddressElement.value = '';
    }

    delete fromElement.dataset.id;
    delete fromElement.dataset.address;
    delete fromElement.dataset.geo;

    delete toElement.dataset.id;
    delete toElement.dataset.address;
    delete toElement.dataset.geo;

    delete additionalAddressElement.dataset.addressList;

    clearMarkers();
}



