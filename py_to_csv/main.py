import csv
import requests
import argparse
import time

NUM = 200
COUNTRIES = ['id', 'in', 'ph']
CATEGORIES = ['FINANCE', 'GAME_CASINO', 'GAME_CARD', 'SHOPPING', 'SOCIAL']
CRAW_URL = 'http://127.0.0.1:3300'

CRAW_APPSTORE_URL = 'http://127.0.0.1:3301'

PKGS = [
"com.upswing.slots",
]

APPSTORE_APPS = [
    "314716233",
]

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


class CrawTopN():
    
    def run(self, countries, categories, num):
        if not countries or not categories or not num:
            raise Exception("params error")

        for c in countries:
            for cate in categories:
                print("args: ", c, cate, num)
                self.get_data(c, cate)


    def get_data(self, country, category):
        data = self.req(country, category)
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
                
    def req(self, country, category):
        u = CRAW_URL + '/api/apps/'
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


class CrawPkgs():
    def run(self, pkgs=[]):
        if not pkgs:
            raise Exception("params pkgs error")

        self.get_data(pkgs)


    def get_data(self, pkgs):
        data = []
        failed_pkgs = []
        for i, pkg in enumerate(pkgs):
            r = self.req(pkg)
            time.sleep(1)
            if not r:
                failed_pkgs.append(pkg)
                continue
            data.append(r)
            print("req success: ", i, pkg, len(pkgs))
        
        print("failed pkgs: ", failed_pkgs)

        transformed_data = []
        for item in data:
            histogram_all = sum([int(i) for i in item.get("histogram", {}).values()])
            transformed_data.append({
                "app_name": item.get("title", ""),
                "package": item.get("appId", ""),
                "category": item.get("genreId", ""), # category名称?
                "provider": item.get("developer", {}).get("devId"),
                "installs": item.get("installs", ""),
                "developerWebsite": item.get("developerWebsite", ""),
                "developerEmail": item.get("developerEmail", ""),
                "adress": item.get("developerAddress", ""),
                #"country": country,
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
                "gplay_url": "https://play.google.com/store/apps/details?id={}".format(item.get("appId", "")),
            })

        # 接下来，我们将数据写入CSV文件
        #name = '{}-{}-output.csv'.format(category, country)
        fname = 'android.csv'
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

    def req(self, pkg, country=""):
        try:
            u = CRAW_URL + '/api/apps/{}/'.format(pkg)
            params = {
                "fullDetail": "true",
                "country": "us",
            }
            res = requests.get(u, params=params)
            if res.status_code != 200:
                raise Exception("status_code err: " + str(res.status_code))
            return res.json()
        except Exception as e:
            print("req exception: ", pkg, e)
            return None


class CrawAppStorePkgs():
    def __init__(self):
        self.store_url = CRAW_APPSTORE_URL
        self.fname = 'appstore.csv'

    def run(self, pkgs=[]):
        if not pkgs:
            raise Exception("params pkgs error")

        self.get_data(pkgs)

    def get_data(self, pkgs):
        data = []
        failed_pkgs = []
        for i, pkg in enumerate(pkgs):
            r = self.req(pkg)
            #time.sleep(1)
            if not r:
                failed_pkgs.append(pkg)
                continue
            data.append(r)
            print("req success: ", i, pkg, len(pkgs))

        print("failed pkgs: ", failed_pkgs)
        transformed_data = []
        keys = ["id", "appId", "title", "url", "description", "icon", "genres", "genreIds", "primaryGenre", "primaryGenreId", "contentRating", "languages", "size", "requiredOsVersion", "released", "updated", "releaseNotes", "version", "price", "currency", "free", "developerId", "developer", "developerUrl", "score", "reviews", "currentVersionScore", "currentVersionReviews", "screenshots", "ipadScreenshots", "appletvScreenshots", "supportedDevices"]
        for item in data:
            tmp = {}
            for k in keys:
                if k not in item:
                    tmp[k] = ""
                    continue
                v = item[k]
                if isinstance(v, str):
                    tmp[k] = v
                elif isinstance(v, list):
                    tmp[k] = "{}".format(v)
                else:
                    tmp[k] = "{}".format(v)
            transformed_data.append(tmp)

        fname = self.fname
        with open(fname, 'w', newline='', encoding='utf-8') as csvfile:
            # 创建一个csv.DictWriter对象，它接受一个文件对象和一个字段名列表
            # 注意：字段名列表需要包含所有将要写入的列名
            # fieldnames = transformed_data[0].keys()
            fieldnames = keys
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # 写入标题行
            writer.writeheader()
            # 遍历转换后的数据列表，并写入每一行
            for row in transformed_data:
                writer.writerow(row)

    def req(self, pkg):
        try:
            u = self.store_url + '/app?id={}'.format(pkg)
            params = {
                "fullDetail": "true",
            }
            res = requests.get(u, params=params)
            if res.status_code != 200:
                raise Exception("status_code err: " + str(res.status_code))
            return res.json()
        except Exception as e:
            print("req exception: ", pkg, e)
            return None


def main(args):
    if args.craw_typ == "topn":
        craw = CrawTopN()
        craw.run(args.countries, args.categories, args.num)
        return
    
    if args.craw_typ == "pkgs":
        craw = CrawPkgs()
        craw.run(args.pkgs)
        return

    if args.craw_typ == "appstore_pkgs":
        craw = CrawAppStorePkgs()
        craw.run(args.appstore_pkgs)
        return

    raise Exception("craw_typ error")

"""
usage: python3 main.py --countries us --categories FINANCE SHOPPING --num 200
usage: python3 main.py --craw_typ pkgs
usage: python3 main.py --craw_typ pkgs
"""
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape Google Play data')
    parser.add_argument('--countries', nargs='+', help='List of countries to scrape', default=COUNTRIES)
    parser.add_argument('--categories', nargs='+', help='List of categories to scrape', default=CATEGORIES)
    parser.add_argument("--num", type=int, help="nums", default=NUM)
    parser.add_argument("--craw_typ", type=str, help="craw type", default="topn")
    parser.add_argument("--pkgs", nargs='+', help='List of pkgs', default=PKGS)
    parser.add_argument("--appstore_pkgs", nargs='+', help='List of pkgs', default=APPSTORE_APPS)

    args = parser.parse_args()
    print("args: ", args)
    main(args)

