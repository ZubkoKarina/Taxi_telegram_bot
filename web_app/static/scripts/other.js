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

    if (button.value === 'Налічні') {
        button.value = 'Карта';
        ico.className = 'fa-regular fa-credit-card button-icon';
    } else {
        button.value = 'Налічні';
        ico.className = 'fas fa-money-bill-wave button-icon';
    }
});
