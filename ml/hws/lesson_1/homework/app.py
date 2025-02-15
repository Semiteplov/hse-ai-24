from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
import pandas as pd
import numpy as np
import joblib
import re

from sklearn.calibration import LabelEncoder
from sklearn.preprocessing import OneHotEncoder

app = FastAPI()

label_encoder = joblib.load("label_encoder.pkl")
ohe = joblib.load("onehotencoder.pkl")
scaler = joblib.load("scaler.pkl")
model = joblib.load("ridge_model.pkl")

with open("feature_names.pkl", "rb") as f:
    feature_names = joblib.load(f)


class Item(BaseModel):
    name: str
    year: int
    km_driven: int
    fuel: str
    seller_type: str
    transmission: str
    owner: str
    mileage: str
    engine: str
    max_power: str
    torque: str
    seats: float


class Items(BaseModel):
    objects: List[Item]


def extract_numeric(value):
    if isinstance(value, str):
        match = re.search(r'([\d.]+)', value)
        return float(match.group(1)) if match else None
    return None


def preprocess_data(data: pd.DataFrame) -> np.ndarray:
    for col in ['mileage', 'engine', 'max_power']:
        data[col] = data[col].apply(extract_numeric)

    if 'torque' in data.columns:
        data[['torque', 'torque_rpm']] = data['torque'].str.extract(
            r'([\d.]+)[^@]*@[\s]?([\d.]+)')
        data['torque'] = pd.to_numeric(data['torque'], errors='coerce')
        data['torque_rpm'] = pd.to_numeric(data['torque_rpm'], errors='coerce')

        data['torque'] = data['torque'].fillna(0)
        data['torque_rpm'] = data['torque_rpm'].fillna(0)

    data['engine'] = data['engine'].fillna(data['engine'].median())
    data['seats'] = data['seats'].fillna(data['seats'].median())
    data['engine'] = data['engine'].astype(int)
    data['seats'] = data['seats'].astype(int)

    data['hp_per_liter'] = data['max_power'] / data['engine']
    data['year_squared'] = data['year'] ** 2
    data['max_power'] = data['max_power'].clip(
        upper=data['max_power'].quantile(0.95))

    for col in ['hp_per_liter', 'max_power', 'mileage', 'hp_per_liter']:
        data[col] = data[col].fillna(data[col].median())

    ohe_columns = ['fuel', 'seller_type', 'transmission', 'owner', 'seats']

    # Label
    known_names = set(label_encoder.classes_)
    data['name'] = data['name'].apply(
        lambda x: x if x in known_names else "unknown")
    data['name'] = label_encoder.transform(data['name'])

    # OHE
    data_ohe = pd.DataFrame(ohe.transform(
        data[ohe_columns]), columns=ohe.get_feature_names_out(ohe_columns))
    data = data.drop(columns=ohe_columns).reset_index(drop=True)
    data = pd.concat([data, data_ohe], axis=1)

    data = data[feature_names]
    data_scaled = scaler.transform(data)

    return data_scaled


@app.post("/predict_item")
def predict_item(item: Item) -> float:
    try:
        input_data = pd.DataFrame([item.model_dump()])
        processed_data = preprocess_data(input_data)
        prediction = model.predict(processed_data)

        return float(prediction[0])
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error in prediction: {str(e)}")


@app.post("/predict_items")
def predict_items(items: Items) -> List[float]:
    try:
        input_data = pd.DataFrame([item.model_dump()
                                  for item in items.objects])
        processed_data = preprocess_data(input_data)
        predictions = model.predict(processed_data)

        return predictions.tolist()
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error in prediction: {str(e)}")


@app.post("/predict_csv")
def predict_csv(file: UploadFile):
    try:
        data = pd.read_csv(file.file)
        processed_data = preprocess_data(data)
        predictions = model.predict(processed_data)

        data['predicted_price'] = predictions

        output_path = "predicted_results.csv"
        data.to_csv(output_path, index=False)

        return FileResponse(
            path=output_path,
            media_type='text/csv',
            filename="predicted_results.csv"
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error processing file: {str(e)}")
