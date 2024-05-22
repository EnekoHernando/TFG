// Cargar la biblioteca de Segment
var analytics = require('analytics-node');
var analyticsClient = new analytics('YOUR_WRITE_KEY');

// Ejemplo de función de registro de evento de Segment
function trackUserEvent(userId, event, properties) {
    analyticsClient.track({
        userId: userId,
        event: event,
        properties: properties
    });
}

// Ejemplo de uso
trackUserEvent('user123', 'Pedido Realizado', {
    orderId: 'order456',
    amount: 100.0,
    currency: 'USD'
});

// Función de personalización en el chatbot
function getUserPreferences(userId, callback) {
    // Recuperar los datos del usuario desde Segment
    analyticsClient.identify({
        userId: userId,
        traits: {
            name: 'John Doe',
            email: 'john.doe@example.com'
        }
    }, function(err, res) {
        if (err) {
            console.error('Error al recuperar las preferencias del usuario:', err);
        } else {
            // Personalizar la respuesta del chatbot basada en las preferencias del usuario
            callback(res);
        }
    });
}

// Ejemplo de personalización de respuesta del chatbot
getUserPreferences('user123', function(userPreferences) {
    console.log('Preferencias del usuario:', userPreferences);
    // Lógica de personalización basada en las preferencias recuperadas
});
