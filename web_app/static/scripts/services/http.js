let userCity = '';

function loadTaxiClasses() {
    fetch('/get-taxi-class')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('select_class_taxi');
            if (!container) {
                console.error('Container not found');
                return;
            }

            data.forEach((item, index) => {
                const block = document.createElement('div');
                block.className = 'block-taxi-class';
                block.dataset.id = item.id; // Збереження id класу таксі в атрибуті даних
                block.dataset.name = item.name;

                const svg = `
                    <svg class="taxi-type-figure" width="65" height="50" viewBox="0 0 65 50" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M0 20C0 8.9543 8.95431 0 20 0H31.6667C35.9941 0 40.2047 1.40356 43.6667 4L57.7778 14.5833V14.5833C72.0848 26.5843 63.7101 50 45.0362 50H20C8.95431 50 0 41.0457 0 30V20Z" fill="#515151"/>
                    </svg>
                `;
                block.innerHTML = svg;

                const img = document.createElement('img');
                img.className = 'taxi-type-img';
                img.src = '../static/images/type_taxi.png';
                img.alt = 'Taxi Type';
                block.appendChild(img);

                const info = document.createElement('span');
                info.id = 'info_taxi_class';
                info.innerHTML = `${item.name}<br>${item.cost} ₴`;
                block.appendChild(info);

                block.addEventListener('click', () => {
                    document.querySelectorAll('.block-taxi-class').forEach(el => el.classList.remove('selected'));
                    block.classList.add('selected');
                    const selectedTaxiClassId = block.dataset.id;
                    console.log('Selected taxi class ID:', selectedTaxiClassId);
                    calculateAndDisplayRoute()
                });

                container.appendChild(block);

                // Зробити перший елемент активним за замовчуванням
                if (index === 0) {
                    block.classList.add('selected');
                }
                const taxiClassBlockActive = document.querySelector('.block-taxi-class.selected');
                console.log(taxiClassBlockActive)
            });
        })
        .catch(error => {
            console.error('Error loading taxi classes:', error);
        });
    }

function loadAdditionalServices() {
    fetch('/additional_services')
        .then(response => response.json())
        .then(data => {
            const additionalServicesList = document.querySelector('.additional-services');
            data.forEach(item => {
                const li = document.createElement('li');

                const button = document.createElement('button');
                button.value = item.name;
                button.innerHTML = `${item.name}<br><small>+${item.cost} ₴</small>`;
                button.dataset.cost = item.cost;
                button.addEventListener('click', function() {
                    button.classList.toggle('selected');
                });

                li.appendChild(button);
                additionalServicesList.appendChild(li);
            });
        })
        .catch(error => {
            console.error('Error loading additional services:', error);
        });
}

function getUserCity() {
    console.log(tg.initDataUnsafe);
    const chat_id = tg.initDataUnsafe.user.id;
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

window.addEventListener('load', loadTaxiClasses);
window.addEventListener('load', loadAdditionalServices);

