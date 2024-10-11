let driverMarkers = [];

function renderDriversInMap(nearby) {
    getDriversNearby(nearby)
        .then(drivers => {
            driverMarkers.forEach(marker => marker.setMap(null));
            driverMarkers = [];

            drivers.forEach(driver => {
                const geo = driver.geo;
                const position = new google.maps.LatLng(geo[0], geo[1]);

                const marker = new google.maps.Marker({
                    position: position,
                    map: map,
                    icon: {
                        url: '../static/images/driver-marker.svg',
                        scaledSize: new google.maps.Size(20, 20)
                    },
                });

                driverMarkers.push(marker);
            });
        })
        .catch(error => {
            console.error('Error fetching nearby drivers:', error);
        });
}