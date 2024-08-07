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


window.addEventListener('load', loadAdditionalServices);
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

    addressModal.classList.add('slide-up');
});

function updatePrice(button) {
    const outputCostElement = document.getElementById('output-cost');
    const outputCost = parseFloat(outputCostElement.value) || 0;
    const serviceCost = parseFloat(button.dataset.cost);
    alert(serviceCost)

    let totalCost = outputCost;

    if (!outputCostElement.dataset.costRoad) {
        totalCost = serviceCost;
    } else {
        totalCost = parseFloat(outputCostElement.dataset.costRoad) + serviceCost;
    }

    outputCostElement.dataset.costServices = serviceCost;
    outputCostElement.value = totalCost;
    outputCostElement.textContent = `${totalCost} грн`;
}


document.getElementById('saveSettingButton').addEventListener('click', function() {
    const selectedServices = [];
    let additionalCost = 0;
    const outputCostElement = document.getElementById('output-cost');
    const outputCost = parseFloat(outputCostElement.value) || 0;

    document.querySelectorAll('.additional-services button.selected').forEach(button => {
        selectedServices.push(button.value + '❗️\n');
        additionalCost += parseFloat(button.dataset.cost);
    });

    const comment_text = document.getElementById('comment').value;
    let full_comment = selectedServices + 'Коментарій: ' + comment_text;

    console.log('Збережені налаштування:', full_comment);

    let totalCost = outputCost;

    if (!outputCostElement.dataset.costRoad) {
        totalCost = additionalCost;
    } else {
        totalCost = parseFloat(outputCostElement.dataset.costRoad) + additionalCost;
    }

    outputCostElement.dataset.costServices = additionalCost;
    outputCostElement.value = totalCost;
    outputCostElement.textContent = `${totalCost} грн`;

    settingModal = document.getElementById('otherSetting')

    settingModal.dataset.comment = full_comment
    settingModal.style.display = 'none';
});
