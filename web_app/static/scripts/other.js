function loadTaxiClasses() {
    fetch('/get-taxi-class')
        .then(response => response.json())
        .then(data => {
            const taxiClassSelect = document.getElementById('class');
            data.forEach(item => {
                const option = document.createElement('option');
                option.value = item.id;
                option.textContent = item.name;
                taxiClassSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error loading taxi classes:', error);
        });
}

window.addEventListener('load', loadTaxiClasses);

document.getElementById('method_pay').addEventListener('click', function() {
    const button = this;
    const ico = document.getElementById('payIco');
    document.getElementById('')

    if (button.value === 'Налічні') {
        button.value = 'Карта';
        ico.className = 'fa-regular fa-credit-card button-icon';
    } else {
        button.value = 'Налічні';
        ico.className = 'fas fa-money-bill-wave button-icon';
    }
});

document.getElementById('edit_price').addEventListener('click', function() {
    const price = parseFloat(document.getElementById('output-cost').value);

    if (!price) {
        alert('Будь ласка, введіть для початку адресу!');
        return;
    }

    const addressModal = document.getElementById("changePrice");
    addressModal.style.display = "block";
    addressModal.classList.add('fade-in');

    const modalContent = document.querySelector('.price-modal-content');
    modalContent.classList.add('slide-up');
    const input_change_price = document.getElementById('changePriceInput');
    const output_price = document.getElementById('outputPrice');

    output_price.textContent = price + ' ₴';
    input_change_price.value = price;
    input_change_price.min = price;
    input_change_price.max = price * 3;
});

document.getElementById('changePriceInput').addEventListener('input', function() {
    const changePriceInput = document.getElementById("changePriceInput");
    const output_price = document.getElementById('outputPrice');

    output_price.textContent = changePriceInput.value + ' ₴';
});

document.getElementById('savePriceButton').addEventListener('click', function() {
    const changePriceInput = document.getElementById("changePriceInput");
    const newPrice = changePriceInput.value;

    document.getElementById('output-cost').value = newPrice;
    document.getElementById('output-cost').textContent = `${newPrice} грн`;

    const addressModal = document.getElementById("changePrice");
    addressModal.style.display = "none";
});

document.getElementById('other').addEventListener('click', function() {
    const addressModal = document.getElementById("otherSetting");
    addressModal.style.display = "block";
    addressModal.classList.add('fade-in');

    const modalContent = document.querySelector('.other-setting-content');
    modalContent.classList.add('slide-up');
});

document.getElementById('saveSettingButton').addEventListener('click', function() {
    const addressModal = document.getElementById("otherSetting");

    addressModal.style.display = "none";
});
