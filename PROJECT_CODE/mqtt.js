const mqtt = require('mqtt');
const fetch = require('node-fetch');

const mqttBroker = 'mqtt://nolane-XPS-9320.local';
const httpServerUrl = 'http://raspberrypi-fr.local:8050';

const client = mqtt.connect(mqttBroker);

client.on('connect', function () {
    console.log('Connected to MQTT broker');

    client.subscribe('TEST');
    // client.subscribe('topic2');
});

client.on('message', function (topic, message) {
    console.log('Received message:', message.toString());
});

function publishSensorData(sensor, data) {
    const topic = `sensors/${sensor}`;
    const payload = JSON.stringify(data);
    const QOS = 1


    client.publish(topic, payload, { qos: QOS }, function (err) {
        if (err) {
            console.error('Error publishing message:', err);
        } else {
            console.log(`Published message to topic ${topic}: ${payload}`);
        }
    });
}

function fetchAndPublishData(sensor) {
    const url = `${httpServerUrl}/${sensor}`;
    fetch(url)
        .then(response => response.json())
        .then(data => {
            publishSensorData(sensor, data);
        })
        .catch(error => {
            console.error('Error fetching data from HTTP server:', error);
        });
}

// Fetch and publish data periodically
setInterval(() => {
    fetchAndPublishData('temperature');
    fetchAndPublishData('mic');
    fetchAndPublishData('light');
    fetchAndPublishData('gas');
    fetchAndPublishData('humidity');
    fetchAndPublishData('pressure');
    fetchAndPublishData("altitude")
},
    10000)

