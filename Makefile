# Makefile
run-dev:
	uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

run-prod:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

clean:
	docker system prune -af

rebuild:
	docker compose down
	docker compose build --no-cache
	docker compose up

test:
	pytest backend/tests

lint:
	ruff backend/app

format:
	black backend/app

install:
	pip install -r backend/requirements.txt

install-dev:
	pip install -r backend/dev-requirements.txt

freeze-dev:
	pip freeze > backend/dev-requirements.txt

freeze-smart:
	pipreqs backend/ --force


