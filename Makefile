build:
	docker build -t longedok/happy_bot .

push:
	docker push longedok/happy_bot

publish:
	docker build -t longedok/happy_bot .
	docker push longedok/happy_bot

run:
	docker-compose up -d --build --no-deps --force-recreate bot

up:
	docker-compose up

test:
	pytest

psql:
	psql -h localhost -p 5432 -U postgres ${POSTGRES_DB}

deploy:
	docker pull longedok/happy_bot
	docker-compose stop bot || true
	docker-compose up -d --no-deps bot

check:
	mypy .

fix:
	isort .
	black .

