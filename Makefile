.PHONY: all build up down test delete logs restart

all:
	docker-compose down
	sleep 3
	docker-compose build
	sleep 3
	docker-compose up -d

down:
	docker-compose down
	
test:
	docker-compose run --rm web pytest app/tests/ -v

delete:
	docker-compose down --volumes --remove-orphans

logs:
	docker-compose logs -f

