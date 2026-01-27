/**
 * Mock Sensor Data Service
 * Generates data dynamically for any room ID
 */

const sensorCache = {};

export function getSensorData(roomId) {
  if (!sensorCache[roomId]) {
    // Init random seed based on ID
    const random = (seed) => {
      var x = Math.sin(seed++) * 10000;
      return x - Math.floor(x);
    };
    // Convert string ID to code or use fallback
    let seed = 123;
    if (typeof roomId === 'string') {
      seed = roomId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    } else if (typeof roomId === 'number') {
      seed = roomId;
    }

    const r = random(seed);

    sensorCache[roomId] = {
      temperature: 20 + (r * 5),
      humidity: 40 + (r * 20),
      occupancy: Math.floor(r * 50) % 15 // 0-14 max occupancy base
    };
  }

  // Simulate slight fluctuation
  const sensor = sensorCache[roomId];

  // Random walk
  sensor.temperature += (Math.random() - 0.5) * 0.5;
  sensor.humidity += (Math.random() - 0.5) * 2;
  // Occupancy changes rarely
  if (Math.random() > 0.9) {
    sensor.occupancy += Math.floor((Math.random() - 0.5) * 3);
  }

  // Bounds
  sensor.temperature = Math.max(18, Math.min(30, sensor.temperature));
  sensor.humidity = Math.max(30, Math.min(70, sensor.humidity));
  sensor.occupancy = Math.max(0, sensor.occupancy);

  return {
    temperature: sensor.temperature.toFixed(1),
    humidity: Math.floor(sensor.humidity),
    occupancy: sensor.occupancy
  };
}