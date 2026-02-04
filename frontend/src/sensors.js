// ================= MQTT SETUP (The Bridge) =================
const MQTT_BROKER = "172.20.10.5";
const MQTT_PORT = 9001;
const CLIENT_ID = "web_sensors_" + Math.floor(Math.random() * 10000);

const TOPIC_MAP = {
  "home/sensors/room401": "401",
  "home/sensors/room402": "402",
  "home/sensors/room403": "403"
};

// Ensure Paho is loaded globally in index.html, or handle import here if using bundlers
const client = new Paho.MQTT.Client(MQTT_BROKER, MQTT_PORT, CLIENT_ID);

client.onConnectionLost = (resp) => console.log("MQTT Lost:", resp.errorMessage);

// WHEN DATA ARRIVES: Update the cache directly
client.onMessageArrived = (message) => {
  const topic = message.destinationName;
  const roomId = TOPIC_MAP[topic];

  if (roomId) {
    try {
      const data = JSON.parse(message.payloadString);
      
      // Initialize cache entry if it doesn't exist
      if (!sensorCache[roomId]) sensorCache[roomId] = {};

      const sensor = sensorCache[roomId];

      // Update values
      if (data.temperature !== undefined) sensor.temperature = parseFloat(data.temperature);
      if (data.humidity !== undefined) sensor.humidity = parseInt(data.humidity);
      if (data.affluence !== undefined) sensor.occupancy = parseInt(data.affluence);

      // FLAG: Mark this as real data so simulation doesn't mess with it
      sensor.isRealData = true; 
      
      console.log(`Updated cache for Room ${roomId}`, sensor);
    } catch (e) {
      console.error("Error parsing MQTT JSON", e);
    }
  }
};

// Connect silently in background
client.connect({
  onSuccess: () => {
    console.log("Sensors.js connected to MQTT");
    for (const t in TOPIC_MAP) client.subscribe(t);
  },
  keepAliveInterval: 30
});

// ================= EXISTING LOGIC (Modified) =================

const sensorCache = {};

export function getSensorData(roomId) {
  // 1. Initialization (Fallback for when page first loads or for simulated rooms)
  if (!sensorCache[roomId]) {
    const random = (seed) => {
      var x = Math.sin(seed++) * 10000;
      return x - Math.floor(x);
    };
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
      occupancy: Math.floor(r * 50) % 15,
      isRealData: false // Default to simulation
    };
  }

  const sensor = sensorCache[roomId];

  // 2. CRITICAL CHANGE: If MQTT provided data, skip simulation logic!
  if (sensor.isRealData) {
    return {
      temperature: Number(sensor.temperature).toFixed(1),
      humidity: Math.floor(sensor.humidity),
      occupancy: sensor.occupancy
    };
  }

  // 3. Fallback Simulation (Only runs if no MQTT data received yet)
  sensor.temperature += (Math.random() - 0.5) * 0.5;
  sensor.humidity += (Math.random() - 0.5) * 2;
  
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