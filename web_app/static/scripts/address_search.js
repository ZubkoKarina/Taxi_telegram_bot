const addressModal = document.getElementById("addressModal");
const searchInput = document.getElementById("searchInput");
const suggestions = document.getElementById("suggestions");
let currentInputId = '';

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
        openAddressModal(e.target.id)
    });
}
if (ToInputElement) {
    ToInputElement.addEventListener('click', (e) => {
        openAddressModal(e.target.id)
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

searchInput.addEventListener('input', function() {
    const query = this.value;
    if (query.length > 2) {
        const service = new google.maps.places.AutocompleteService();
        service.getPlacePredictions({
            input: query,
            componentRestrictions: { country: 'UA' },
            types: ['address'],
            location: new google.maps.LatLng(50.7472, 25.3254),
            radius: 50000
        }, (predictions, status) => {
            if (status !== google.maps.places.PlacesServiceStatus.OK || !predictions) {
                return;
            }

            suggestions.innerHTML = '';
            predictions.forEach((prediction) => {
                if (prediction.description.toLowerCase()) {
                    const li = document.createElement('li');
                    li.innerHTML = `<strong>${prediction.terms[0].value} ${prediction.terms[1].value}</strong><br><small>${prediction.terms[2].value}</small>`;
                    li.onclick = () => {
                        document.getElementById(currentInputId).value = `${prediction.terms[0].value}, ${prediction.terms.slice(1).map(term => term.value).join(', ')}`;
                        addressModal.style.display = "none";
                        handleAddressSelection(prediction.description, currentInputId === 'to');
                    };
                    suggestions.appendChild(li);
                }
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
    });
}
