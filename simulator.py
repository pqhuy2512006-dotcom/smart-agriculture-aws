import json
import random
import time
from datetime import datetime

DEVICE_ID = "sensor_greenhouse_01"

def generate_sensor_data():
    """Giả lập dữ liệu cảm biến nông nghiệp"""
    soil_moisture = round(random.uniform(18.0, 55.0), 2)
    temperature = round(random.uniform(24.0, 38.0), 2)
    humidity = round(random.uniform(50.0, 85.0), 2)
    
    payload = {
        "device_id": DEVICE_ID,
        "timestamp": int(time.time()),
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "soil_moisture": soil_moisture,
        "temperature": temperature,
        "humidity": humidity
    }
    return payload

if __name__ == "__main__":
    print(f"=== BẮT ĐẦU CHẠY THIẾT BỊ GIẢ LẬP ({DEVICE_ID}) ===")
    print("Nhấn Ctrl+C để dừng script khi không làm việc.\n")
    try:
        while True:
            data = generate_sensor_data()
            print(f"[SEND MQTT] -> Topic 'greenhouse/sensors/data': {json.dumps(data)}")
            time.sleep(10) # Gửi dữ liệu định kỳ 10s/lần
    except KeyboardInterrupt:
        print("\n=== ĐÃ DỪNG GIẢ LẬP ===")