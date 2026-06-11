from fastapi import FastAPI
from app.schema import CarFeatures,PredictionResponse
from fastapi.responses import JSONResponse
from app.model import predict_price,load_artifacts


app = FastAPI(title="Car Price Prediction API",version="1.0")

@app.on_event("startup")
def startup_event():
    load_artifacts()

@app.get("/")
def test():
    return JSONResponse(status_code=200,content={ "success":True,"message":"this is test route"})    



@app.post("/predict",response_model=PredictionResponse)
def predict(features:CarFeatures):
    price = predict_price(features.model_dump())
    return PredictionResponse(prediction_price=price)  

