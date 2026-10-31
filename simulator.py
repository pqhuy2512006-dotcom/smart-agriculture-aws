import json
import random
import time
from datetime import datetime
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# --- CẤU HÌNH THÔNG SỐ (THAY THẾ BẰNG THÔNG TIN CỦA BẠN) ---
ENDPOINT = "auagqaduhejbq-ats.iot.us-east-1.amazonaws.com"  # Thay bằng IoT Endpoint từ Settings
CLIENT_ID = "sensor_greenhouse_01"
PATH_TO_CERT = "certs/device-certificate.pem.crt"
PATH_TO_KEY = "certs/private.pem.key"
PATH_TO_ROOT_CA = "certs/AmazonRootCA1.pem"
TOPIC_DATA = "greenhouse/sensors/data"
TOPIC_CONTROL = "greenhouse/pump/control"

# Callback khi nhận được lệnh điều khiển máy bơm từ Lambda/Cloud
def on_message_received(client, userdata, message):
    payload = json.loads(message.payload.decode('utf-8'))
    print(f"\n[RECEIVED MQTT COMMAND] <- Topic '{message.topic}':")
    print(json.dumps(payload, indent=2))
    print(f">>> HỆ THỐNG GIẢ LẬP: Thực hiện hành động -> {payload.get('action')} trong {payload.get('duration_sec', 0)}s <<<\n")

# Khởi tạo MQTT Client
mqtt_client = AWSIoTMQTTClient(CLIENT_ID)
mqtt_client.configureEndpoint(ENDPOINT, 8883)
mqtt_client.configureCredentials(PATH_TO_ROOT_CA, PATH_TO_KEY, PATH_TO_CERT)

# Cấu hình kết nối
mqtt_client.configureAutoReconnectBackoffTime(1, 32, 20)
mqtt_client.configureOfflinePublishQueueing(-1)
mqtt_client.configureDrainingFrequency(2)
mqtt_client.configureConnectDisconnectTimeout(10)
mqtt_client.configureMQTTOperationTimeout(5)

print("Đang kết nối tới AWS IoT Core...")
mqtt_client.connect()
print("Kết nối thành công!")

# Subscribe lệnh điều khiển máy bơm
mqtt_client.subscribe(TOPIC_CONTROL, 1, on_message_received)

try:
    while True:
        # Giả lập thông số
        # soil_moisture = round(random.uniform(10.0, 60.0), 2)
        # temperature = round(random.uniform(25.0, 38.0), 2)
        # humidity = round(random.uniform(50.0, 80.0), 2)
        
        # KỊCH BẢN 1: Độ ẩm đất rất thấp ( 20% < soil_moisture) -> Bật máy bơm, Gửi hộp thư email
        soil_moisture = 15.0  # Cố định độ ẩm > 30%
        temperature = 28.5
        humidity = 65.0


        telemetry = {
            "device_id": CLIENT_ID,
            "timestamp": int(time.time()),
            "datetime_utc": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "soil_moisture": soil_moisture,
            "temperature": temperature,
            "humidity": humidity
        }
        
        mqtt_client.publish(TOPIC_DATA, json.dumps(telemetry), 1)
        print(f"[PUBLISH MQTT] -> Topic '{TOPIC_DATA}': Soil Moisture={soil_moisture}% | Temp={temperature}°C")
        time.sleep(10)
except KeyboardInterrupt:
        print("\nNgắt kết nối AWS IoT Core...")
        mqtt_client.disconnect()