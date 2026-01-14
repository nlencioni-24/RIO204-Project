// sensors.js
// Données simulées pour toutes les salles
window.sensorData = {
  "401": { temperature: 21, humidity: 45, occupancy: 0 },
  "402": { temperature: 24, humidity: 55, occupancy: 10 },
  "403": { temperature: 22, humidity: 50, occupancy: 5 }
};

// Simulation de changement toutes les 5 secondes
function simulateSensors() {
  for (const id in sensorData) {
    const sensor = sensorData[id];
    // variation aléatoire
    sensor.temperature += Math.floor(Math.random() * 5 - 2); // ±2°C
    sensor.humidity += Math.floor(Math.random() * 11 - 5);    // ±5%
    sensor.occupancy += Math.floor(Math.random() * 5 - 2);    // ±2 personnes

    // bornes
    if (sensor.temperature < 15) sensor.temperature = 15;
    if (sensor.temperature > 30) sensor.temperature = 30;
    if (sensor.humidity < 20) sensor.humidity = 20;
    if (sensor.humidity > 80) sensor.humidity = 80;
    if (sensor.occupancy < 0) sensor.occupancy = 0;
    if (sensor.occupancy > 50) sensor.occupancy = 50;
  }
}

// Actualisation automatique
setInterval(simulateSensors, 5000);