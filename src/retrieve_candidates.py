import pandas as pd
import json
from google import genai
import chromadb

GET_TOP_N_PATENTS = 20
GENERATE_TOP_N_PRODUCT_CHUNKS = 1   # 跑N个product
GENERATE_TOP_N_COMPANIES = 1        # 如果你也想限制company，就保留；不想就设很大

client = genai.Client(api_key=api_key)
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection("patents")

df = pd.read_json("company_product_data.json")

output = {}
count_products = 0
count_companies = 0

for row in df["companies"]:
    company_name = str(row.get("name", "")).strip()

    for product in row.get("products", []):
        product_name = str(product.get("name", "")).strip()
        product_desc = str(product.get("description", "")).strip()

        
        product_chunk = f"[Company] {company_name}\n[Product] {product_name}\n[Description] {product_desc}".strip()

        print(product_chunk)
        print(15 * "-")

        vec = embed_with_retry(client, product_chunk, max_retries=3)
        if vec is None:
            print(f"[跳过] {company_name} - {product_name} embedding 多次失败")
            continue

        res = collection.query(
            query_embeddings=[vec],
            n_results=GET_TOP_N_PATENTS,
            include=["metadatas", "distances"]
        )

        ids = res.get("ids", [[]])[0]
        dists = res.get("distances", [[]])[0]
        metas = res.get("metadatas", [[]])[0]

        top_list = []
        for pid, dist, meta in zip(ids, dists, metas):
            top_list.append({
                "patent_id": pid,
                "distance": dist,
                "meta": meta
            })

        product_key = f"{company_name}||{product_name}"
        output[product_key] = {
            "company": company_name,
            "product": product_name,
            "product_chunk": product_chunk,
            "top_patents": top_list
        }

        print(f"[OK] {product_key} -> top{GET_TOP_N_PATENTS} patents")

        count_products += 1
        if count_products >= GENERATE_TOP_N_PRODUCT_CHUNKS:
            break

    count_companies += 1
    if count_products >= GENERATE_TOP_N_PRODUCT_CHUNKS:
        break
    if count_companies >= GENERATE_TOP_N_COMPANIES:
        break

with open("candidates_top20_test.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("Done! saved to candidates_top20_test.json")
