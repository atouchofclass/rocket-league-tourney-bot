pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                echo 'Building..'
                sh "pip3 install -r requirements.txt"
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
                sh "export BUILD_ID=dontKillMe"
                sh "export JENKINS_NODE_COOKIE=dontKillMe"
                sh "chmod +x ./start_pm2.sh"
                sh "chmod +x ./stop_pm2.sh"
                sh "./stop_pm2.sh || true"
                sh "./start_pm2.sh"
            }
        }
    }
}