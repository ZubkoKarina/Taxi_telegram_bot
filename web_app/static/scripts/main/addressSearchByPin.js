let isListenMoveMap = false
let addressToSave = null
const blockMap = document.getElementById('map');

document.addEventListener("DOMContentLoaded", function () {
    const addMarkerButton = document.querySelector(".bt-search-address");
    addMarkerButton.addEventListener("click", function () {
        if (typeof map === 'undefined') {
            console.error("Map is not initialized");
            return;
        }
        isListenMoveMap = true
        MoveMarker(true);
    });

    const savePlaceButton = document.getElementById('confirm-place-button');
    savePlaceButton.addEventListener("click", function () {
        const otherSettingText = document.querySelector(".other-setting-text").textContent;
        const pinDiv = document.getElementById('main-marker');

        pinDiv.classList.remove('active');
        pinDiv.classList.add('deactive');

        searchInputElement = document.getElementById(currentInputId)
        if (currentInputId == 'from' || currentInputId == 'to') {
            searchInputElement.querySelector('span').innerText = addressToSave.address;
            searchInputElement.dataset.id = addressToSave.id
            searchInputElement.dataset.address = addressToSave.address
            searchInputElement.dataset.geo = JSON.stringify(addressToSave.geo)
            placeMarker(addressToSave.geo[0], addressToSave.geo[1])
        }
        if (markers.length != 0 && currentInputId == 'from') {
            clearAddress()
        }
        if (currentInputId == 'add-stop-button') {
            let addressList = searchInputElement.dataset.addressList ? JSON.parse(searchInputElement.dataset.addressList) : [];
            addressList.push({
                address: addressToSave.address,
                id: addressToSave.id,
                geo: addressToSave.geo
            });
            searchInputElement.dataset.addressList = JSON.stringify(addressList);
            placeMarker(addressToSave.geo[0], addressToSave.geo[1])
        }


        if (markers.length >= 2) {
            closeAddressSearchByPinModal();
            openSelectionAddressFull();
        } else {
            closeAddressSearchByPinModal();
            openSelectionAddress();
        }

        if (currentInputId === 'to' || currentInputId === 'add-stop-button') {
            isListenMoveMap = false
            pinDiv.remove()
        };
    });
});

let moveTimeout = null;

function MoveMarker(isFullFunction) {
    const pinDiv = document.getElementById('main-marker');
    const controlPanel = document.getElementById('container-main-menu');

    if (pinDiv) {
        pinDiv.remove();
    }

    map.setZoom(17);
    if (isFullFunction) {
        closeSearchAddressModal();
        openAddressSearchByPinModal();
    }

    searchFromElement = document.getElementById(currentInputId);
    if (!searchFromElement.dataset.geo) {
        searchFromElement = document.getElementById('from');
    }
    if (searchFromElement.dataset.geo) {
        const geoData = JSON.parse(searchFromElement.dataset.geo);
        const lat_marker = geoData[0];
        const lng_marker = geoData[1];
        map.setCenter(new google.maps.LatLng(lat_marker, lng_marker));
    }

    Promise.all([
        fetch('../static/images/map-pin-active.svg').then(response => response.text()),
        fetch('../static/images/map-pin-deactive.svg').then(response => response.text())
    ])
    .then(([activeSvg, deactiveSvg]) => {
        const pinDiv = document.createElement('div');
        pinDiv.classList.add('pin');
        pinDiv.id = 'main-marker';
        pinDiv.classList.add('marker-icon');
        pinDiv.innerHTML = deactiveSvg;
        pinDiv.classList.add('deactive');
        blockMap.appendChild(pinDiv);

        map.addListener('dragstart', function () {
            if (!isListenMoveMap) {
                return;
            }
//            pinDiv.innerHTML = activeSvg;
            if (pinDiv.classList.contains('deactive')) {
                pinDiv.classList.remove('deactive');
                pinDiv.classList.add('active');
                pinDiv.innerHTML = activeSvg;
            }

            if (moveTimeout) {
                clearTimeout(moveTimeout);
            }
        });

        map.addListener('idle', function () {
            if (!isListenMoveMap) {
                return;
            }

            moveTimeout = setTimeout(function () {
                pinDiv.innerHTML = deactiveSvg;
                pinDiv.classList.remove('active');
                pinDiv.classList.add('deactive');

                const center = map.getCenter();
                let lat = center.lat();
                let lng = center.lng();
                getAddressByGeo(lat, lng);
                if (currentInputId == 'from') {
                    renderDriversInMap([center.lat(), center.lng()])
                }

            }, 500);
        });

    })
    .catch(error => {
        console.error('Error loading SVG icons:', error);
    });
}


function getAddressByGeo(lat, lng) {

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
        addressToSave = data
        addressToSave.geo = [lat, lng]
        document.querySelector(".other-setting-text").innerHTML = addressToSave.name;
        if (currentInputId == 'from') {
            searchInputElement = document.getElementById('from')
            searchInputElement.querySelector('span').innerText = addressToSave.address;
            searchInputElement.dataset.id = addressToSave.id
            searchInputElement.dataset.address = addressToSave.address
            searchInputElement.dataset.geo = JSON.stringify([lat, lng])
        }
    });
};


