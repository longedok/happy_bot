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

check:
	mypy .

fix:
	isort .
	black .

