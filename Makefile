build:
		docker-compose -f ./deployment/db/docker-compose.yml up --build


up:
		docker-compose -f ./deployment/db/docker-compose.yml up -d

down:
		docker-compose -f ./deployment/db/docker-compose.yml down

runserver:
		uvicorn app:app --reload --workers=1

run: up runserver
