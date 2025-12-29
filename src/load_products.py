import pandas as pd
# 把原来的数据展开
df = pd.read_json("company_product_data.json")
companies = df["companies"]
out = []
for row in companies:
    company_name = row["name"]

    for product in row["products"]:
        out.append({"company":company_name, "product_name":product["name"], "product_description":product["description"]})
df = pd.DataFrame(out)
df.to_markdown("data_schema.md", index=False)
