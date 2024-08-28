import csv  
import json  
import requests

NUM = 10

def req(country, category):
    u = 'http://127.0.0.1:3000/api/apps/'
    params = {
        "category": category,
        "country": country,
        "num": NUM,
        "fullDetail": "true",
        "collection": "TOP_FREE",
    }
    res = requests.get(u, params=params)
    if res.status_code != 200:
        raise Exception("status_code err")
    return res.json()["results"]


# kv = {
#     "app_name": "title",
#     "package": "appId",
#     "category": "--",
#     "provider": "developerId",
#     "installs": "installs",
#     "developerWebsite": "developerWebsite",
#     "developerEmail": "developerEmail",
#     "adress": "developerAddress",
#     "country": "--",
#     "score": "score",
#     "ratings": "ratings",
# }

def main():
    countries = ['id', 'in', 'ph']
    categories = ['FINANCE', 'GAME_CASINO', 'GAME_CARD', 'SHOPPING', 'SOCIAL']
    for c in countries:
        for cate in categories:
            getdata(c, cate)

def getdata(country='id', category='GAME_CARD'):
    data = req(country, category)
    transformed_data = []
    for item in data:
        transformed_data.append({
            "app_name": item.get("title", ""),
            "package": item.get("appId", ""),
            "category": category,
            "provider": item.get("developerId", ""),
            "installs": item.get("installs", ""),
            "developerWebsite": item.get("developerWebsite", ""),
            "developerEmail": item.get("developerEmail", ""),
            "adress": item.get("developerAddress", ""),
            "country": country,
            "score": item.get("score", ""),
            "ratings": item.get("ratings", ""),
        })
    
    # 接下来，我们将数据写入CSV文件  
    with open('{}-{}-output.csv'.format(category, country), 'w', newline='', encoding='utf-8') as csvfile:  
        # 创建一个csv.DictWriter对象，它接受一个文件对象和一个字段名列表  
        # 注意：字段名列表需要包含所有将要写入的列名  
        fieldnames = transformed_data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)  
    
        # 写入标题行  
        writer.writeheader()  
    
        # 遍历转换后的数据列表，并写入每一行  
        for row in transformed_data:  
            writer.writerow(row)  


if __name__ == "__main__":
    main()