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

    routeConstruction()
}

function closeMainMenu() {

    controlPanel = document.getElementById('main-menu-container')
    controlPanel.classList.remove('slide-up')
    controlPanel.classList.add('folding-down')
    setTimeout(() => {
        controlPanel.style.display = 'none'

        controlPanel = document.getElementById('map')
        controlPanel.style.height = '70%'
        controlPanel.classList.remove('folding-down')
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