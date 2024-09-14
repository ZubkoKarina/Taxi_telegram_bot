let tg = window.Telegram.WebApp;
tg.expand();

document.getElementById('place-order-button').addEventListener('click', () => {
    const dataFrom = document.getElementById('from').dataset;
    const dataTo = document.getElementById('to').dataset;

    let stopList = [];
    if (document.getElementById('add-stop-button')) {
        stopList = JSON.parse(document.getElementById('add-stop-button').dataset.addressList || '[]');
    }

    const taxiClassBlockActive = document.querySelector('.block-taxi-class.selected');
    const taxiClassId = taxiClassBlockActive.dataset.id;
    const taxiClassName = taxiClassBlockActive.dataset.name;

    const button_pay = document.getElementById('payment-method-button').value;
    const price = document.getElementById('output-cost').value;
    const variable = document.getElementById('output-cost').dataset.variable;
    const comment = document.getElementById('additional-settings-modal').dataset.comment;

    if (!dataFrom || !dataTo || !taxiClassId) {
        showNotification('Будь ласка, заповніть всі поля перед замовленням.');
        return;
    }

    if (button_pay === 'Карта') {
        fetch('/online_payment', {
            method: 'GET'
        })
        .then(response => response.json())
        .then(data => {
            if (!data) {
                showNotification('Наразі оплата карткою не доступна');
                return;
            } else {
                sendOrderData({
                    user_chat_id: tg.initDataUnsafe.user.id,
                    start_point: {
                        id: dataFrom.id,
                        geo_lng: JSON.parse(dataFrom.geo)[1],
                        geo_lat: JSON.parse(dataFrom.geo)[0],
                        address: dataFrom.address
                    },
                    end_point: {
                        id: dataTo.id,
                        geo_lng: JSON.parse(dataTo.geo)[1],
                        geo_lat: JSON.parse(dataTo.geo)[0],
                        address: dataTo.address
                    },
                    additional_point: stopList,
                    taxiClass: {
                        id: taxiClassId,
                        name: taxiClassName
                    },
                    payment_method: button_pay,
                    cost: price,
                    comment: comment,
                    variable:  JSON.parse(variable)
                });
            }
        })
        .catch(error => {
            console.error('Error checking online payment:', error);
        });
    } else {
        sendOrderData({
            user_chat_id: tg.initDataUnsafe.user.id,
            start_point: {
                id: dataFrom.id,
                geo_lng: JSON.parse(dataFrom.geo)[1],
                geo_lat: JSON.parse(dataFrom.geo)[0],
                address: dataFrom.address
            },
            end_point: {
                id: dataTo.id,
                geo_lng: JSON.parse(dataTo.geo)[1],
                geo_lat: JSON.parse(dataTo.geo)[0],
                address: dataTo.address
            },
            additional_point: stopList,
            taxiClass: {
                id: taxiClassId,
                name: taxiClassName
            },
            payment_method: button_pay,
            cost: price,
            comment: comment,
            variable:  JSON.parse(variable)
        });
    }
});

function sendOrderData(orderData) {
    console.log('Sending order data:', orderData);

    fetch('/send_order_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(orderData)
    })
    .catch(error => {
        console.error('Error sending order data:', error);
    });

    // Закриваємо веб-додаток одразу після відправлення запиту
    tg.close()
}


function log(message) {
    fetch(`/log?message=${message}`);
}

function showNotification(textNotification) {
    const notification = document.getElementById('notification');
    const textNotificationElement = document.getElementById('notification-message');
    textNotificationElement.textContent = textNotification;
    notification.classList.add('show');
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}
