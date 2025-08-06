check:
	ruff check .

fix:
	ruff check --fix .

format:
	ruff format .

api:
	python3 asgi.py

docker_build:
	docker-compose up -d --build

docker_up:
	docker-compose up -d

docker_start:
	docker-compose start

docker_down:
	docker-compose down

docker_destroy:
	docker-compose down -v

docker_stop:
	docker-compose stop

docker_restart:
	docker-compose stop
	docker-compose up -d

docker_logs:
	docker-compose logs --tail=100 -f

docker_prune:
	docker image prune