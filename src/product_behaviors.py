from pydantic import BaseModel, Field
from google import genai
from typing import List, Optional
import pandas as pd
import json

df_1 = pd.read_json("company_product_data.json")
out_path = "product_behaviors.jsonl" #输出路径

class Behavior(BaseModel):
    feature: str = Field(..., description="User-visible feature")
    user_action: str = Field(..., description="Action performed by the user")
    system_action: str = Field(..., description="Action performed by the system")
    inputs: List[str] = Field(..., description="Inputs required for the behavior")
    outputs: List[str] = Field(..., description="Outputs produced by the behavior")
    triggers: List[str] = Field(..., description="Events that trigger the behavior")


class ProductBehavior(BaseModel):
    company: str = Field(..., description="Company name")
    product: str = Field(..., description="Product name")
    behaviors: List[Behavior] = Field(..., description="List of product behaviors")


client = genai.Client(api_key = api_key)

with open(out_path, "w", encoding="utf-8") as f:
    
    for company in df_1["companies"]:
        company_name = company["name"]
        for product in company["products"]:
            prompt = f"""
You are a product analyst. Output must follow the JSON schema exactly.
Company:
{company_name}
Product:
{product["name"]}
Product Description:
{product["description"]}
""".strip()        

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_json_schema": ProductBehavior.model_json_schema(),
                },
            )
    
            parsed = json.loads(response.text)
            parsed["company"] = company_name
            parsed["product"] = product["name"]
            
            f.write(json.dumps(parsed, ensure_ascii=False) + "\n")
            print(f'公司{company_name}的产品{product["name"]}已处理完毕')
