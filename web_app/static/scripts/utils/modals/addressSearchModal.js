var FromInputElement = document.getElementById('from');
var ToInputElement = document.getElementById('to');
var AdditionalAddressElement = document.getElementById('add-stop-button');

if (FromInputElement) {
    FromInputElement.addEventListener('click', (e) => {
        closeSelectionAddress()

        setTimeout(() => {
            openSearchAddressModal(e.target.id);
        }, 200);

    });
}
if (ToInputElement) {
    ToInputElement.addEventListener('click', (e) => {
        closeSelectionAddress()
        setTimeout(() => {
            openSearchAddressModal(e.target.id);
        }, 200);
    });
}

if (AdditionalAddressElement) {
    AdditionalAddressElement.addEventListener('click', (e) => {
        closeSelectionAddress()
        setTimeout(() => {
            openSearchAddressModal(e.target.id);
        }, 200);
    });
}

//window.onclick = function(event) {
//    if (event.target == addressModal) {
//        closeSearchAddressModal()
//        openSelectAddressModal()
//    }
//}

function openSearchAddressModal(inputId) {
    searchAddressModal = document.getElementById('address-search-modal')
    searchBlock = document.getElementById('address-search-block')

    searchAddressModal.classList.add('fade-in');

    searchBlock.classList.add('slide-down');
    currentInputId = inputId;
    searchAddressModal.style.display = "flex";
    searchInput.value = '';
    suggestions.innerHTML = '';
    searchInput.focus();
}

function closeSearchAddressModal() {
    searchAddressModal = document.getElementById('address-search-modal')
    searchAddressModal.style.display = "none";
}