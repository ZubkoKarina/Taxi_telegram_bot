function openAddressSearchByPinModal() {
    const blockMap = document.getElementById('map');
    const searchPlaceByMarker = document.getElementById('place-confirmation-block');

    blockMap.style.height = '100%';
    setTimeout(() => {
        searchPlaceByMarker.classList.add('slide-up')
        searchPlaceByMarker.style.display = 'block';
    }, 100);
}

function closeAddressSearchByPinModal() {
    const placeConfirmationBlock = document.getElementById('place-confirmation-block');

    setTimeout(() => {
        placeConfirmationBlock.style.display = "none";
    }, 100);
}