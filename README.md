# Flask ML CI/CD Project

Iris species predictor (Flask + Random Forest) with a Jenkins CI/CD pipeline,
Docker deployment and Prometheus + Grafana monitoring.

## Run locally
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    python app.py

## Run tests
    python -m pytest -v

## Docker
    docker build -t flask-ml-app .
    docker run -d -p 5000:5000 --name flask-ml-app flask-ml-app

## Full stack (App + Prometheus + Grafana)
    docker rm -f flask-ml-app
    docker compose up -d --build

- App: http://localhost:5000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin / admin)

## API test
    curl -X POST http://localhost:5000/api/predict -H "Content-Type: application/json" -d "{\"sepal_length\":5.1,\"sepal_width\":3.5,\"petal_length\":1.4,\"petal_width\":0.2}"
