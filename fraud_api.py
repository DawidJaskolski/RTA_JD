from fastapi import FastAPI
from pydantic import BaseModel
import pickle, numpy as np

app = FastAPI(title="Fraud Detection API")
model = pickle.load(open('fraud_model.pkl', 'rb'))

class Transaction(BaseModel):
    amount: float
    hour: int
    is_electronics: int
    tx_per_day: int

# TWÓJ KOD
# Endpoint POST /score
# Przyjmij Transaction, zwróć: {"is_fraud": bool, "fraud_probability": float}

@app.post("/score")
def predict_fraud(transaction: Transaction):
    # 1. Konwersja danych z obiektu Pydantic na format akceptowany przez model (2D array)
    data = [[
        transaction.amount,
        transaction.hour,
        transaction.is_electronics,
        transaction.tx_per_day
    ]]

    # 2. Predykcja klasy (0 lub 1)
    prediction = model.predict(data)[0]

    # 3. Predykcja prawdopodobieństwa (wyciągamy wartość dla klasy 1 - fraud)
    probability = model.predict_proba(data)[0][1]

    # 4. Zwrócenie wyniku zgodnego z wymaganiami zadania
    return {
        "is_fraud": bool(prediction),
        "fraud_probability": float(probability)
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "timestamp": str(datetime.now())
    }
