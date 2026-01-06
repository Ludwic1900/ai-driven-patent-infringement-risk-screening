You are a patent claims analyst. Output must follow the JSON schema exactly.
Title:
{test_item.get("title", "")}        
Abstract:
{test_item.get("abstract", "")} 
Claim:
{claim_text}
