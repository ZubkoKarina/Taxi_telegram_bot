 const addressModal = document.getElementById("addressModal");
const searchInput = document.getElementById("searchInput");
const suggestions = document.getElementById("suggestions");
const geoButton = document.getElementById("user-geo")
let currentInputId = '';

function openAddressModal(inputId) {
    controlPanel = document.getElementById('container_selection_address')
    blockMap = document.getElementById('map')

    currentInputId = inputId;
    controlPanel.style.display = 'none'
    addressModal.style.display = "flex";
    addressModal.classList.add('slide-up');
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

//document.querySelector('.close').onclick = function() {
//    addressModal.style.display = "none";
//}

window.onclick = function(event) {
    if (event.target == addressModal) {
        addressModal.style.display = "none";

        controlPanel = document.getElementById('container_selection_address')
        controlPanel.style.display = 'grid'
    }
}

let timeout = null;

searchInput.addEventListener('input', function() {
    clearTimeout(timeout);

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
                    const searchInputElement = document.getElementById(currentInputId);

                    const isStreet = address.categories === 'adr_street';
                    if (isStreet) {
                        outputAddressNumbers(address.id)
                    } else {
                        searchInputElement.value = address.name;
                        searchInputElement.dataset.id =  address.id
                        searchInputElement.dataset.address = address.address
                        addressModal.style.display = "none";

                        const controlPanel = document.getElementById('container_selection_address');
                        controlPanel.style.display = 'grid';

                        handleAddressSelection(address.id, currentInputId === 'to');
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
                const searchInputElement = document.getElementById(currentInputId);

                searchInputElement.value = address.address;
                searchInputElement.dataset.id = address.id
                searchInputElement.dataset.address = address.address
                addressModal.style.display = "none";

                controlPanel = document.getElementById('container_selection_address')
                controlPanel.style.display = 'grid'

                handleAddressSelection(address.id, currentInputId === 'to');

            }
            suggestions.appendChild(li);
        });
    })
    .catch(error => {
        console.error('Error:', error);
    });
};

function handleAddressSelection(place_id, isDestination) {
    geocodeAddress(place_id, isDestination, (location) => {
        document.getElementById(currentInputId + '_lat').value = location.lat;
        document.getElementById(currentInputId + '_lng').value = location.lng;
        if (!isDestination) {
            MoveMarker(false);
        }
        map.setZoom(18)
        if (isDestination) {
            openMainMenu();
        }
    });
}

