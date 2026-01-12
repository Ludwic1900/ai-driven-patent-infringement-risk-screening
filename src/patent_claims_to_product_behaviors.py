from pydantic import BaseModel, Field
from google import genai
from typing import List, Optional
import pandas as pd
import json

top_N = 20 #选择前20个专利
df_1 = pd.read_json("patents.json")
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
    
    for i in range(top_N):
    
        row = df_1.iloc[i]
        test_item = row.to_dict() #将这一行数据变为字典，方便后续处理
        publication_num = test_item.get("publication_number","")
        claims_list = json.loads(test_item["claims"]) #读取claim部分
        #print(claims_list[-3:])
        for claim in claims_list:
            claim_text = claim["text"] # 原始 claim 句子
            print(f"正在处理{claim_num}专利数据")
    
            prompt = f"""
You are a patent claims analyst. Output must follow the JSON schema exactly.
Title:
{test_item.get("title", "")}        
Abstract:
{test_item.get("abstract", "")} 
Claim:
{claim_text}
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
            
            f.write(json.dumps(parsed, ensure_ascii=False) + "\n")
        print(f'公开文件ID：{test_item.get("id","")}已处理完毕')
