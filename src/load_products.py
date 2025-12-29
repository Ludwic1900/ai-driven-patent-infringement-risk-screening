import pandas as pd
MAX_LEN = 10 #限制字段最大的长度

df_1 = pd.read_json("patents.json")
df_show = df_1.copy().astype(str).apply(lambda col: col.str.slice(0, MAX_LEN) + "...") #裁剪了每个字段
df_show.to_markdown("data_schema.md", index=False)
