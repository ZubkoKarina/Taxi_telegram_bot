document.getElementById('method_pay').addEventListener('click', function() {
    const button = this;
    const image = document.getElementById('payImage');

    if (button.value === 'Налічні') {
        button.value = 'Карта';
        image.src = 'static/images/card.png';
    } else {
        button.value = 'Налічні';
        image.src = 'static/images/money.png';
    }
});
