build:
	docker build . -t gpapi:latest

run:
	docker run --rm -it --name gpapi -p 3300:3300 gpapi:latest
