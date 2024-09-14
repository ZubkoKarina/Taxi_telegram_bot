function clearMarkers() {
    for (let i = 0; i < markers.length; i++) {
        markers[i].setMap(null);
        if (markers[i].infoWindow) {
            markers[i].infoWindow.onRemove(); // Видаляємо інфовікно
        }
        if (directionsRenderer) {
            directionsRenderer.setDirections({ routes: [] });
        }
    }
    markers = [];
}



function placeMarker(lat, lng) {
    if (currentInputId === 'from') {
        return
    }
    if (markers.length == 0) {
        searchFromElement = document.getElementById('from')
        const geoData = JSON.parse(searchFromElement.dataset.geo);
        const marker_from = new google.maps.Marker({
            position: { lat: geoData[0], lng: geoData[1] },
            icon: {
                url: '../static/images/from-marker-second.svg',
                scaledSize: new google.maps.Size(20, 20)
            },
            map: map
        });
        markers.push(marker_from);
        addTittle(marker_from);
        openSelectionAddressFull()
    }

    const marker = new google.maps.Marker({
        position: { lat: lat, lng: lng },
        map: map,
        icon: {
            url: '../static/images/to-marker-second.svg',
            scaledSize: new google.maps.Size(20, 20)
        }
    });
    markers.push(marker);
    addTittle(marker);

    const bounds = new google.maps.LatLngBounds();
    markers.forEach((marker) => {
        bounds.extend(marker.getPosition());
    });
    map.fitBounds(bounds);
}