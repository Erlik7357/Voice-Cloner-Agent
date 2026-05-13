.PHONY: install dev-backend dev-frontend test lint docker-up clean

# Install all dependencies (backend + frontend)
install:
	pip install -r backend/requirements.txt
	cd dashboard && npm install

# Run Flask backend server
dev-backend:
	python backend/tts_server.py

# Run Vite frontend dev server
dev-frontend:
	cd dashboard && npm run dev

# Run all tests
test:
	python -m pytest tests/ -v

# Run linters
lint:
	ruff check backend/ tests/
	cd dashboard && npx tsc --noEmit

# Build dashboard for production
build:
	cd dashboard && npm run build

# Docker
docker-up:
	docker-compose up --build

docker-down:
	docker-compose down

# Remove generated files
clean:
	rm -rf output/cache/*.wav
	rm -rf dashboard/dist
	rm -rf __pycache__ backend/__pycache__ tests/__pycache__
