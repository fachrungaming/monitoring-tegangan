import sqlite3
import os

DB_NAME = "voltage_monitor.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Table for Device Configuration
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS device_config (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_name TEXT DEFAULT 'ESP32_Voltage_Monitor',
        location TEXT DEFAULT 'Living Room',
        mqtt_topic TEXT DEFAULT 'elban/voltage/data',
        v_low_threshold REAL DEFAULT 200.0,
        v_high_threshold REAL DEFAULT 240.0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Insert default config if not exists
    cursor.execute("SELECT COUNT(*) FROM device_config")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
        INSERT INTO device_config (device_name, location) VALUES (?, ?)
        ''', ('ESP32 Monitor', 'Main Panel'))

    # Table for History Data (Voltage, Current, Power, Energy, etc)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sensor_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        voltage REAL,
        current REAL,
        power REAL,
        energy REAL,
        frequency REAL,
        pf REAL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database '{DB_NAME}' initialized successfully.")

if __name__ == "__main__":
    init_db()
