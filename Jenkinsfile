pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                echo 'Building..'
            }
        }
        stage('Test') {
            steps {
                echo 'Testing..'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying....'
                sh "chmod +x ./start_pm2.sh"
                sh "chmod +x ./stop_pm2.sh"
                sh "./start_pm2.sh"
            }
        }
    }
}