import json 
with open("test.json", "r") as f:
    content = f.read()
    cj = json.loads(content)
    print(f"total: {len(cj)}")
    for item in cj:
        print(f"{item['name']}")