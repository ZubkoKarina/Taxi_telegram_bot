document.addEventListener("DOMContentLoaded", function () {
    const addMarkerButton = document.querySelector(".bt-search-address");
    addMarkerButton.addEventListener("click", function () {
        if (typeof map === 'undefined') {
            console.error("Map is not initialized");
            return;
        }

        MoveMarker(true);
    });

    const savePlaceButton = document.getElementById('savePlaceButton');
    savePlaceButton.addEventListener("click", function () {
        const latElement = document.getElementById(currentInputId + '_lat');
        const lngElement = document.getElementById(currentInputId + '_lng');
        const activeInput = document.getElementById(currentInputId);
        const otherSettingText = document.querySelector(".other-setting-text").textContent;
        const centerMarkerDiv = document.getElementById('main_marker');

        centerMarkerDiv.classList.remove('active');
        centerMarkerDiv.classList.add('deactive');
        closeModal();
        console.log(activeInput)
        if (activeInput.id == 'to') {
            openMainMenu();
        };
    });
});

function closeModal() {
    const addressModal = document.getElementById('addressModal');
    const controlPanel = document.getElementById('container_selection_address');
    const searchPlaceByMarker = document.getElementById('search-place-by-marker');
    const userGeo = document.getElementById('user-geo');

    addressModal.style.display = "none";
    controlPanel.style.display = 'grid';
    searchPlaceByMarker.style.display = 'none';
    userGeo.style.display = 'block';
}

function MoveMarker(isFullFunction) {
    const centerMarkerDiv = document.getElementById('main_marker');
    const controlPanel = document.getElementById('container_main_menu')
    const blockMap = document.getElementById('map');
    const addressSearch = document.getElementById('addressModal');
    const searchPlaceByMarker = document.getElementById('search-place-by-marker');
    const userGeo = document.getElementById('user-geo');

    if (centerMarkerDiv) {
        centerMarkerDiv.remove()
    }
    if (controlPanel.style.display === 'grid'){
        return
    }
    map.setZoom(17)
    if (isFullFunction) {
        blockMap.style.height = '100%';
        searchPlaceByMarker.style.display = 'block';
        userGeo.style.display = 'none';
        addressSearch.style.display = "none";
    }

    let lat_marker = document.getElementById('from_lat').value;
    let lng_marker = document.getElementById('from_lng').value;
    console.log(lat_marker, lng_marker)
    if (lat_marker && lng_marker) {
        map.setCenter(new google.maps.LatLng(lat_marker, lng_marker));
    }

    // Fetch the SVG files
    Promise.all([
        fetch('../static/images/map-pin-active.svg').then(response => response.text()),
        fetch('../static/images/map-pin-deactive.svg').then(response => response.text())
    ])
    .then(([activeSvg, deactiveSvg]) => {
        const centerMarkerDiv = document.createElement('div');
        centerMarkerDiv.classList.add('center-marker');
        centerMarkerDiv.id = 'main_marker'
        centerMarkerDiv.classList.add('marker-icon'); // Adding base class for animation
        centerMarkerDiv.innerHTML = deactiveSvg; // Default to deactive
        centerMarkerDiv.classList.add('deactive');
        blockMap.appendChild(centerMarkerDiv);

        // Add event listener for starting drag
        map.addListener('dragstart', function () {
            centerMarkerDiv.innerHTML = activeSvg;
            centerMarkerDiv.classList.remove('deactive');
            centerMarkerDiv.classList.add('active');
        });

        // Add event listener for stopping drag
        map.addListener('idle', function () {
            setTimeout(function () {
                centerMarkerDiv.innerHTML = deactiveSvg;
                centerMarkerDiv.classList.remove('active');
                centerMarkerDiv.classList.add('deactive');

                const center = map.getCenter();
                let lat = center.lat();
                let lng = center.lng();
                if (controlPanel.style.display !== 'grid'){
                    getAddressByGeo(lat, lng);
                }
            }, 700);
        });

    })
    .catch(error => {
        console.error('Error loading SVG icons:', error);
    });
}

function getAddressByGeo(lat, lng) {
    let place = null;

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
        document.querySelector(".other-setting-text").innerHTML = place.name;

        const activeInput = document.getElementById(currentInputId);
        if (activeInput) {
            activeInput.value = place.address;
            activeInput.dataset.id = place.id
            activeInput.dataset.address = place.address
            document.getElementById(activeInput.id + '_lat').value = lat;
            document.getElementById(activeInput.id + '_lng').value = lng;
        } else {
            searchInputElement = document.getElementById('from')
            searchInputElement.value = place.name;
            searchInputElement.dataset.id = place.id
            searchInputElement.dataset.address = place.address
            document.getElementById('from_lat').value = lat;
            document.getElementById('from_lng').value = lng;
        }
    });
};


