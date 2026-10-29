import time
from flask import Flask, request, jsonify, render_template, Response
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from prometheus_client import (Counter, Histogram, generate_latest,
                               CONTENT_TYPE_LATEST)

app = Flask(__name__)

# ---------- Model (trained on first start) ----------
iris = load_iris()
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(iris.data, iris.target)
SPECIES = list(iris.target_names)
FEATURES = ["sepal_length", "sepal_width", "petal_length", "petal_width"]

# ---------- Prometheus metrics ----------
REQUESTS = Counter("app_requests_total", "HTTP requests per endpoint", ["endpoint"])
PREDICTIONS = Counter("app_predictions_total", "Predictions per species", ["species"])
ERRORS = Counter("app_prediction_errors_total", "Invalid prediction requests")
LATENCY = Histogram("app_prediction_latency_seconds", "Prediction latency in seconds")


def predict_species(values):
    start = time.time()
    idx = int(model.predict([values])[0])
    species = SPECIES[idx]
    LATENCY.observe(time.time() - start)
    PREDICTIONS.labels(species=species).inc()
    return species


def parse_values(data):
    values = []
    for f in FEATURES:
        v = float(data[f])
        if v <= 0 or v > 100:
            raise ValueError("out of range")
        values.append(v)
    return values


@app.route("/")
def home():
    REQUESTS.labels(endpoint="/").inc()
    return render_template("index.html", result=None, error=None, form={})


@app.route("/predict", methods=["POST"])
def predict_form():
    REQUESTS.labels(endpoint="/predict").inc()
    try:
        values = parse_values(request.form)
        species = predict_species(values)
        return render_template("index.html", result=species, error=None, form=request.form)
    except (KeyError, ValueError, TypeError):
        ERRORS.inc()
        return render_template("index.html", result=None,
                               error="Please enter valid positive numbers in all fields.",
                               form=request.form), 400


@app.route("/api/predict", methods=["POST"])
def api_predict():
    REQUESTS.labels(endpoint="/api/predict").inc()
    data = request.get_json(silent=True) or {}
    try:
        values = parse_values(data)
    except (KeyError, ValueError, TypeError):
        ERRORS.inc()
        return jsonify(error="Provide numeric sepal_length, sepal_width, "
                             "petal_length, petal_width"), 400
    return jsonify(species=predict_species(values))


@app.route("/health")
def health():
    REQUESTS.labels(endpoint="/health").inc()
    return jsonify(status="ok")


@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
