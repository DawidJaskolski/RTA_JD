from kafka import KafkaConsumer, KafkaProducer
from datetime import datetime
import json, requests

consumer = KafkaConsumer('transactions', bootstrap_servers='broker:9092',
    auto_offset_reset='earliest', group_id='ml-scoring',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')))

alert_producer = KafkaProducer(bootstrap_servers='broker:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8'))

API_URL = "http://localhost:8001/score"

# TWÓJ KOD
# Dla każdej transakcji:
# 1. Wyciągnij cechy (amount, hour z timestamp, is_electronics, tx_per_day=5)
# 2. requests.post(API_URL, json=features)
# 3. Jeśli is_fraud: wyślij do tematu 'alerts', wypisz ALERT

for message in consumer:
    transaction = message.value

    # 1. Wyciągnij cechy (ekstrakcja godziny z timestampu)
    # Zakładamy, że timestamp jest w formacie ISO, np. "2026-04-18T08:30:00"
    dt = datetime.fromisoformat(transaction['timestamp'])

    features = {
        "amount": transaction['amount'],
        "hour": dt.hour,
        "is_electronics": transaction['is_electronics'],
        "tx_per_day": 5  # wartość stała zgodnie z poleceniem
    }

    # 2. Odpytanie API (Scoring)
    try:
        response = requests.post(API_URL, json=features)
        prediction = response.json()

        # 3. Jeśli model wykrył fraud, wyślij alert do tematu 'alerts'
        if prediction.get("is_fraud"):
            alert_payload = {
                "transaction_id": transaction.get("id", "N/A"),
                "amount": transaction['amount'],
                "probability": prediction.get("fraud_probability"),
                "timestamp": transaction['timestamp']
            }

            alert_producer.send('alerts', value=alert_payload)
            print(f"ALERT: Wykryto oszustwo! Prawdopodobieństwo: {prediction.get('fraud_probability'):.2f}")

    except Exception as e:
        print(f"Błąd podczas łączenia z API: {e}")
