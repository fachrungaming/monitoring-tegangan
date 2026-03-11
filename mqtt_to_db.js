const mqtt = require('mqtt');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

// MQTT Configuration
const MQTT_BROKER = "mqtt://broker.hivemq.com";
const MQTT_TOPIC = "elban/voltage/data";
const DB_NAME = "voltage_monitor.db";

// Connect to SQLite
const dbPath = path.resolve(__dirname, DB_NAME);
const db = new sqlite3.Database(dbPath, (err) => {
    if (err) {
        console.error("Error opening database:", err.message);
    } else {
        console.log("Connected to SQLite database.");
    }
});

function saveToDb(data) {
    const query = `
        INSERT INTO sensor_history (voltage, current, power, energy, frequency, pf)
        VALUES (?, ?, ?, ?, ?, ?)
    `;
    const params = [
        data.voltage,
        data.current,
        data.power,
        data.energy,
        data.frequency,
        data.pf
    ];

    db.run(query, params, function (err) {
        if (err) {
            return console.error("❌ Database Insert Error:", err.message);
        }
        console.log(`✅ [DB SAVE SUCCESS] ID: ${this.lastID} | Voltage: ${data.voltage}V | Power: ${data.power}W`);
    });
}

// Connect to MQTT
const client = mqtt.connect(MQTT_BROKER);

let isAutoSaveEnabled = true;
let logInterval = 10000; // Default 10 seconds
let lastSaveTime = 0;

client.on('connect', () => {
    console.log("Connected to MQTT Broker");
    client.subscribe(MQTT_TOPIC);
    client.subscribe("elban/config/autosave");
    client.subscribe("elban/config/log_interval");
    console.log(`Subscribed to: ${MQTT_TOPIC} and config topics`);
});

client.on('message', (topic, message) => {
    if (topic === "elban/config/autosave") {
        isAutoSaveEnabled = message.toString() === "1";
        console.log(`Auto Save Setting: ${isAutoSaveEnabled ? 'ENABLED' : 'DISABLED'}`);
        return;
    }

    if (topic === "elban/config/log_interval") {
        const intervalInSeconds = parseInt(message.toString());
        if (!isNaN(intervalInSeconds)) {
            logInterval = intervalInSeconds * 1000;
            console.log(`Database Log Interval set to: ${intervalInSeconds} seconds`);
        }
        return;
    }

    if (topic === MQTT_TOPIC) {
        try {
            const data = JSON.parse(message.toString());
            const now = Date.now();
            const timeDiff = now - lastSaveTime;

            if (!isAutoSaveEnabled) {
                // Log only occasionally or at a lower priority if it was disabled
                return;
            }

            if (timeDiff >= logInterval) {
                console.log(`📥 [MQTT DATA] Saving to DB... (Interval: ${logInterval / 1000}s, Last save: ${Math.round(timeDiff / 1000)}s ago)`);
                saveToDb(data);
                lastSaveTime = now;
            } else {
                // Optional: verbose logging for skipped records
                // console.log(`⏩ [SKIP] Recording skipped. Next save in ${Math.round((logInterval - timeDiff)/1000)}s`);
            }
        } catch (e) {
            console.error("❌ JSON Parse Error:", e.message);
        }
    }
});

process.on('SIGINT', () => {
    db.close((err) => {
        if (err) {
            console.error(err.message);
        }
        console.log('Closed the database connection.');
        process.exit(0);
    });
});
