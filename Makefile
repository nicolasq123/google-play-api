build:
	docker build . -t gpapi:latest

run:
	docker run --rm -itd --name gpapi -p 3300:3300 gpapi:latest

logs:
	docker logs -f gpapi
