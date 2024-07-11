document.getElementById('method_pay').addEventListener('click', function() {
    const button = this;
    const image = document.getElementById('payImage');

    if (button.value === 'cash') {
        button.value = 'card';
        image.src = 'static/images/card.png';
    } else {
        button.value = 'cash';
        image.src = 'static/images/money.png';
    }
});
