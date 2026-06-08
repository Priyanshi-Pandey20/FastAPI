from fastapi import FastAPI,HTTPException,Query,Path
from services.products import get_all_products
from pydantic import BaseModel
app = FastAPI()

@app.get("/") # static route - which will give you same output every time you run it
def root():
    return{"message":"Welcome to FastApi"}


# # @app.get("/products") #dynamic route 
# def get_products():
#     return get_all_products()

#we are taking out products after doing filterout 
@app.get("/products")
def list_products(name:str=Query(
default=None,
min_length=1, max_length=50,
description="Search by product name(case insensitive)"
),
sort_by_price:bool = Query(
    default=False,description="Sort products by price"),
    order: str = Query("asc",description="Sort order when sort_by_price=true (asc,desc)"),
    limit:int = Query(default=10,ge=1,le=100,description="No. of items to return "),
    offset:int = Query(default=0,ge=0,description="Pagination offset")

):
    products = get_all_products()
    if name:
        needle = name.strip().lower()
        products = [p for p in products if needle in p.get("name","").lower()]

    if not products:
        raise HTTPException(status_code=404,detail=f"No product found matching name = {name}")
        
    if sort_by_price:
        reverse = order =="desc"
        products = sorted(products,key=lambda p:p.get("price",0),reverse=reverse)
        
    total = len(products)
    products = products[offset:offset+limit]

    return {
        "total":total,
        "limit":limit,
        "items":products
    }

#get product by id 
@app.get("/products/{product_id}")
def get_product_by_id(product_id:str=Path(
    ...,min_length=36,max_length=36,description="UUID of the product",example="Energy 3Pcs",

)):
    products = get_all_products()
    for product in products:
        if product["id"] == product_id:
            return product
    raise HTTPException(status_code=404,detail="Product not found")    

class Product(BaseModel): #this is how we insert our data 
    id:str
    sku:str
    name:str

@app.post("/products",status_code=201)
def create_product(product:Product):
    return product