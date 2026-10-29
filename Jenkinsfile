pipeline {
    agent any

    environment {
        IMAGE_NAME = 'flask-ml-app'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '''
                python -m venv venv
                venv\\Scripts\\python -m pip install --upgrade pip
                venv\\Scripts\\pip install -r requirements.txt
                '''
            }
        }

        stage('Test') {
            steps {
                bat 'venv\\Scripts\\python -m pytest -v'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat '''
                docker build -t %IMAGE_NAME%:%BUILD_NUMBER% -t %IMAGE_NAME%:latest .
                '''
            }
        }

        stage('Deploy') {
            steps {
                bat '''
                docker rm -f flask-ml-app 2>nul || exit /b 0
                docker compose up -d --build
                '''
            }
        }

        stage('Verify') {
            steps {
                sleep time: 15, unit: 'SECONDS'
                bat 'curl -f http://localhost:5000/health'
            }
        }
    }

    post {
        success { echo 'Pipeline succeeded - app, Prometheus and Grafana are running.' }
        failure { echo 'Pipeline failed - check the console output.' }
    }
}
