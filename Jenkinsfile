pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                // Pull latest code from the repository
                checkout scm
            }
        }

        stage('Run Tests') {
            steps {
                // Run the unit tests
                sh 'python -m unittest discover -s test/'
            }
        }

        stage('Prepare for Deploy') {
            steps {
                // Copy the test module to the main project directory and rename
                sh 'cp test/test_cleanse_data_module.py your_project_name/cleanse_data_module.py'
            }
        }

        stage('Build Docker Image') {
            steps {
                // Login to DockerHub
                withCredentials([usernamePassword(credentialsId: 'dockerhub_credentials', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                    sh 'docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD'
                }
                // Build the Docker image
                sh 'docker build -t thaibigdata/cicd_for_realtime_data_pipeline:latest .'
                
                // Push the Docker image to your registry
                sh 'docker push thaibigdata/cicd_for_realtime_data_pipeline:latest'
            }
        }
    }

    post {
        success {
            echo 'All stages completed successfully!'
        }
        failure {
            echo 'Something went wrong!'
        }
    }
}
