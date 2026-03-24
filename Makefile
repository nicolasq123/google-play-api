build:
	docker build . -t gpapi:latest

run:
	docker run --rm -itd --name gpapi -p 3300:80 gpapi:latest

logs:
	docker logs -f gpapi

run_craw_android_pkgs:
	cd py_to_csv && python3 main.py --craw_typ pkgs
