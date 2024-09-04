import csv
import json
import requests

NUM = 1000 # 200
COUNTRIES = ['id', 'in', 'ph']
CATEGORIES = ['FINANCE', 'GAME_CASINO', 'GAME_CARD', 'SHOPPING', 'SOCIAL']

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
        raise Exception("status_code err" + str(res.status_code))
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
    countries = COUNTRIES
    categories = CATEGORIES
    for c in countries:
        for cate in categories:
            get_data(c, cate)

def get_data(country, category):
    data = req(country, category)
    print("get the data", country, category, len(data))
    transformed_data = []
    for item in data:
        histogram_all = sum([int(i) for i in item.get("histogram", {}).values()])
        transformed_data.append({
            "app_name": item.get("title", ""),
            "package": item.get("appId", ""),
            "category": category,
            "provider": item.get("developer", {}).get("devId"),
            "installs": item.get("installs", ""),
            "developerWebsite": item.get("developerWebsite", ""),
            "developerEmail": item.get("developerEmail", ""),
            "adress": item.get("developerAddress", ""),
            "country": country,
            "score": round(item.get("score", 0), 2),
            "score1_ratio": round(item.get("histogram", {}).get("1", 0) / histogram_all, 2) if histogram_all else 0,
            "score2_ratio": round(item.get("histogram", {}).get("2", 0) / histogram_all, 2) if histogram_all else 0,
            "score3_ratio": round(item.get("histogram", {}).get("3", 0) / histogram_all, 2) if histogram_all else 0,
            "score4_ratio": round(item.get("histogram", {}).get("4", 0) / histogram_all, 2) if histogram_all else 0,
            "score5_ratio": round(item.get("histogram", {}).get("5", 0) / histogram_all, 2) if histogram_all else 0,
            "score1_num": item.get("histogram", {}).get("1", 0),
            "score2_num": item.get("histogram", {}).get("2", 0),
            "score3_num": item.get("histogram", {}).get("3", 0),
            "score4_num": item.get("histogram", {}).get("4", 0),
            "score5_num": item.get("histogram", {}).get("5", 0),
            "ratings": item.get("ratings", ""),
            "gplay_url": "https://play.google.com/store/apps/details?id={}&gl={}".format(item.get("appId", ""), country),
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