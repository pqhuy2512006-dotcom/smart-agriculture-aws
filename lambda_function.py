import json
import time
import os
import boto3

iot_data = boto3.client('iot-data')
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

DYNAMODB_TABLE = 'SoilIrrigationHistory'
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN', '')
CONTROL_TOPIC = 'greenhouse/pump/control'
SOIL_THRESHOLD_LOW = 30.0  # Độ ẩm < 30% sẽ bật máy bơm

def lambda_handler(event, context):
    print("Received MQTT Event:", json.dumps(event))
    
    device_id = event.get('device_id', 'unknown_device')
    soil_moisture = float(event.get('soil_moisture', 0.0))
    temperature = float(event.get('temperature', 0.0))
    current_time = int(event.get('timestamp', time.time()))
    
    pump_status = "OFF"
    
    # 1. Logic bật máy bơm nếu độ ẩm thấp
    if soil_moisture < SOIL_THRESHOLD_LOW:
        pump_status = "ON"
        
        control_payload = {
            "device_id": device_id,
            "action": "PUMP_ON",
            "duration_sec": 30,
            "reason": f"Soil moisture low ({soil_moisture}%)",
            "timestamp": current_time
        }
        iot_data.publish(
            topic=CONTROL_TOPIC,
            qos=1,
            payload=json.dumps(control_payload)
        )
        print(f"Issued PUMP_ON command to {CONTROL_TOPIC}")

        # 2. Gửi Cảnh báo qua SNS nếu độ ẩm rất thấp (< 20%)
        if soil_moisture < 20.0 and SNS_TOPIC_ARN:
            alert_message = (
                f"⚠️ CANH BAO DO AM DAT THAP ⚠️\n"
                f"Thiet bi: {device_id}\n"
                f"Do am dat: {soil_moisture}%\n"
                f"Nhiet do: {temperature}°C\n"
                f"Trang thai: Da phat lenh tuoi!"
            )
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject="[ALERT] Canh bao tuoi cay!",
                Message=alert_message
            )

    # 3. Ghi thông tin vào DynamoDB
    table = dynamodb.Table(DYNAMODB_TABLE)
    table.put_item(
        Item={
            'device_id': device_id,
            'timestamp': current_time,
            'soil_moisture': str(soil_moisture),
            'temperature': str(temperature),
            'pump_status': pump_status,
            'datetime_utc': event.get('datetime_utc', '')
        }
    )

    return {'statusCode': 200, 'body': 'OK'}