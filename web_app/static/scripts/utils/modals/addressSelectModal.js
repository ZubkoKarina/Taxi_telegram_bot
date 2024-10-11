function openSelectionAddress() {
    const controlPanelSelection = document.getElementById('address-selection-container');
    controlPanelSelection.style.display = 'flex';

    const mapPanel = document.getElementById('map');
    mapPanel.style.height = '100%';

    const userGeo = document.getElementById('geo-location-button');
    userGeo.style.display = 'block';

    controlPanelSelection.classList.add('slide-up')
}

function closeSelectionAddress() {
    const controlPanelSelection = document.getElementById('address-selection-container');

    controlPanelSelection.classList.add('folding-down')
    setTimeout(() => {
            document.getElementById('add-stop-button').style.display = "none";
            document.getElementById('continue-button').style.display = "none";
            controlPanelSelection.style.display = 'none';
            const userGeo = document.getElementById('geo-location-button');
            userGeo.style.display = 'none';
            controlPanelSelection.classList.remove('folding-down')
    }, 200);
}

function openSelectionAddressFull() {
    const controlPanelSelection = document.getElementById('address-selection-container');
    controlPanelSelection.style.display = 'flex';

    const mapPanel = document.getElementById('map');
    mapPanel.style.height = '100%';

    const userGeo = document.getElementById('geo-location-button');
    userGeo.style.display = 'block';

    document.getElementById('add-stop-button').style.display = "block";
    document.getElementById('continue-button').style.display = "block";
}

