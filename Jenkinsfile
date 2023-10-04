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
                // Build the Docker image
                sh 'docker build -t your_docker_repo_name/your_project_name:latest .'
                
                // Push the Docker image to your registry
                sh 'docker push your_docker_repo_name/your_project_name:latest'
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
