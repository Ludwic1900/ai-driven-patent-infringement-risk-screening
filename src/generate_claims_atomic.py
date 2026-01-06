from pydantic import BaseModel, Field
from google import genai
from typing import List, Optional
import pandas as pd
import json

top_N = 20 #选择前20个专利
df_1 = pd.read_json("patents.json")
out_path = "claims_atomic.jsonl" #输出路径

class Element(BaseModel): #这是输出用的格式的一部分
    actor: Optional[str] = Field(description="Who performs the action.")
    action: Optional[str] = Field(description="What action is performed.")
    object: Optional[str] = Field(description="What the action is performed on.")
    condition: Optional[str] = Field(description="Condition under which the action occurs.")
    data: Optional[List[str]] = Field(description="Data involved in this element.")

class YourSchema(BaseModel): #这是输出用的格式
    claim_num: str = Field(description="Publication number + claim number.") #这个值不需要LLM计算
    sub: str = Field(description="The title of the patent.")
    abstract: str = Field(description="The abstract of the patent.")
    elements:List[Element]
    must_have: List[str] = Field(
        description="Essential technical features that must be present to satisfy the claim."
    )
    optional: List[str] = Field(
        description="Optional or alternative features described in the claim."
    )
    notes: str = Field(
        description="Additional notes, interpretations, or clarifications about the claim."
    )


client = genai.Client(api_key = api_key)

with open(out_path, "w", encoding="utf-8") as f:
    
    for i in range(top_N):
    
        row = df_1.iloc[i]
        test_item = row.to_dict() #将这一行数据变为字典，方便后续处理
        publication_num = test_item.get("publication_number","")
        claims_list = json.loads(test_item["claims"]) #读取claim部分
        for claim in claims_list:
            claim_text = claim["text"] # 原始 claim 句子
            claim_num_raw = claim["num"] # 比如"00001"           
            claim_num = publication_num + "-" + str(claim_num_raw) #把publication number 和 claim numeber 整合了
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
                    "response_json_schema": YourSchema.model_json_schema(),
                },
            )
    
            parsed = json.loads(response.text)
            parsed["claim_num"] = claim_num #把之前算的claim_num代入json中
            f.write(json.dumps(parsed, ensure_ascii=False) + "\n")
        print(f"公开文件ID：{test_item.get("ID","")}已处理完毕")
