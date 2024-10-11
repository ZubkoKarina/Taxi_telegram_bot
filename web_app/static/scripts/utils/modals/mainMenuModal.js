function openMainMenu() {

    const pinDiv = document.getElementById('main-marker');
    if (pinDiv) {
        pinDiv.remove()
    }

    controlPanel = document.getElementById('main-menu-container')
    controlPanel.classList.add('slide-up')
    controlPanel.style.display = 'grid'

    controlPanel = document.getElementById('map')
    controlPanel.style.height = '70%'

    markerUserGeo.setMap(null)
    routeConstruction()
}

function closeMainMenu() {

    controlPanel = document.getElementById('main-menu-container')
    document.getElementById("output-cost").classList.remove('visible');
    controlPanel.classList.remove('slide-up')
    controlPanel.classList.add('folding-down')
    setTimeout(() => {
        controlPanel.classList.remove('folding-down')
        controlPanel.style.display = 'none'
        controlPanel = document.getElementById('map')
        controlPanel.style.height = '70%'

    }, 200);
}

document.getElementById('change-address-button').addEventListener('click', () => {
    clearAddress()
    closeMainMenu()
    openSelectionAddress()
});

document.getElementById('continue-button').addEventListener('click', () => {
    closeSelectionAddress()
    setTimeout(() => {
        openMainMenu();
    }, 300);
});