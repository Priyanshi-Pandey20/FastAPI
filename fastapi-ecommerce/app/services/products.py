import json
from pathlib import Path
from typing import List,Dict

DATA_FILE = Path(__file__).parent.parent / "data" / "dummy.json"

def load_products() -> List[Dict]:
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE,'r',encoding='utf-8') as file:
        return json.load(file)
    
def get_all_products() -> List[Dict]:
    return load_products()    

def save_product(products:List[Dict])-> None:
    with open(DATA_FILE,"w",encoding="utf-8") as f:
        json.dump(products,f,indent=2,ensure_ascii=False)

def add_product(product:Dict) -> Dict:
    products = get_all_products()

    if any(p["sku"] == product["sku"] for p in products):
        raise ValueError("SKU already exists")

    products.append(product)
    save_product(products)
    return product        



    