up:
	docker compose up --build -d
down:
	docker compose down -v
logs:
	docker compose logs -f
backendLogs:
	docker compose logs -f backend
frontendLogs:	
	docker compose logs -f frontend
ollamaserve:
	ollama serve