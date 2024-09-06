function openMainMenu() {
    controlPanel = document.getElementById('container_selection_address')
    controlPanel.style.display = 'none'

    const centerMarkerDiv = document.getElementById('main_marker');
    if (centerMarkerDiv) {
        centerMarkerDiv.remove()
    }

    controlPanel = document.getElementById('container_main_menu')
    controlPanel.style.display = 'grid'

    controlPanel = document.getElementById('map')
    controlPanel.style.height = '70%'

    const userGeo = document.getElementById('user-geo');
    userGeo.style.display = 'none';

    calculateAndDisplayRoute()
}

function openSelectionAddress() {
    const controlPanelSelection = document.getElementById('container_selection_address');
    controlPanelSelection.style.display = 'grid';

    const controlPanelMainMenu = document.getElementById('container_main_menu');
    controlPanelMainMenu.style.display = 'none';

    const mapPanel = document.getElementById('map');
    mapPanel.style.height = '100%';

    const userGeo = document.getElementById('user-geo');
    userGeo.style.display = 'block';

    document.getElementById('from').value = '';
    document.getElementById('to').value = '';

    const outputCost = document.getElementById('output-cost');
    outputCost.dataset.cost = '';
    outputCost.value = '';
    directionsRenderer.setDirections({ routes: [] });
    markers.forEach(marker => marker.setMap(null));
}

document.getElementById('change_address').addEventListener('click', openSelectionAddress);