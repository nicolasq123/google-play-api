build:
	docker build . -t registry.umlife.net:443/adxmi/adn/gpapi:latest

run:
	docker run --rm -it --name gpapi -p 80:80 registry.umlife.net:443/adxmi/adn/gpapi:latest

push:
	docker push registry.umlife.net:443/adxmi/adn/gpapi:latest
