import csv
import requests
from conf import CRAW_GOOGLE_STORE_URL


# country-lang-search
TargetData = [
    ['id', 'id', 'Pinjaman'],
    ['ng', 'en', 'loan'],
    ['in', 'en', 'loan'],
    ['th', 'th', 'เงินกู้'],
    ['vn', 'vi', 'khoản vay'],
    ['br', 'pt', 'empréstimo'],
]


"""
1. 根据"国家, 语言,关键词" 爬取,  过滤"掉分数,评论数",
2. 但是一次最多30条,有点麻烦
"""
class CrawSearchGP():
    def __init__(self):
        self.store_url = CRAW_GOOGLE_STORE_URL
        self.fname = 'appstore.csv'

    def run(self):
        for i in TargetData:
            gl, hl, search =i[0], i[1], i[2]
            data = self.req(gl, hl, search)
            results = data['results']
            print("req suc: ", gl, hl, search, len(results))

            fmtd = self.fmt_data(results, gl, hl, True)
            if not fmtd:
                print("no target data:", gl, hl, search, len(fmtd))

            fname = "./csv/{}-{}-{}-output.csv".format(gl, hl, search)
            self.gen_csv(fname,fmtd)

    
    def fmt_data(self, results, gl, hl, filter=False):
        transformed_data = []
        for item in results:
            pkg = item.get("appId", "")
            histogram_all = sum([int(i) for i in item.get("histogram", {}).values()])
            if filter:
                score = round(item.get("score", 0), 2)
                if not (3.5 <= score <= 4.5):
                    print("score continue: ", pkg, score)
                    continue

                if not (5000 <= histogram_all <= 50000):
                    print("score_num continue: ", pkg, histogram_all)
                    continue

            transformed_data.append({
                "app_name": item.get("title", ""),
                "package": item.get("appId", ""),
                "category": item.get("genreId", ""),
                "provider": item.get("developer", {}).get("devId"),
                "installs": item.get("installs", ""),
                "developerWebsite": item.get("developerWebsite", ""),
                "developerEmail": item.get("developerEmail", ""),
                "adress": item.get("developerAddress", ""),
                #"country": country,
                "score": round(item.get("score", 0), 2),
                "score_num": histogram_all, 
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
                "gplay_url": "https://play.google.com/store/apps/details?id={}&gl={}&hl={}".format(item.get("appId", ""), gl, hl),
            })
        
        return transformed_data


    def gen_csv(self, fname, transformed_data):
        with open(fname, 'w', newline='', encoding='utf-8') as csvfile:
            # 创建一个csv.DictWriter对象，它接受一个文件对象和一个字段名列表
            # 注意：字段名列表需要包含所有将要写入的列名
            fieldnames = transformed_data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # 写入标题行
            writer.writeheader()

            # 遍历转换后的数据列表，并写入每一行
            for row in transformed_data:
                writer.writerow(row)

    def req(self, gl, hl, search):
        try:
            u = self.store_url
            params = {
                "gl": gl,
                "hl": hl,
                "q": search, # Pinjaman
                "num": 100, # max 30?
                "fullDetail": "true",
            }
            res = requests.get(u, params=params)
            if res.status_code != 200:
                raise Exception("status_code err: " + str(res.status_code))
            return res.json()
        except Exception as e:
            print("req exception: ", u, params, e)
            return None

if __name__ == "__main__":
    craw = CrawSearchGP()
    craw.run()