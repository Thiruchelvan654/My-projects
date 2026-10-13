pipeline {
  agent any

  options {
    disableConcurrentBuilds()
  }

  // GitHub can't reach a Jenkins on your laptop, so Jenkins checks the repo itself
  triggers {
    pollSCM('H/5 * * * *')
  }

  environment {
    BACKEND_IMAGE  = 'dockerthiru6/my-project-backend'
    FRONTEND_IMAGE = 'dockerthiru6/my-project-frontend'
  }

  stages {
    stage('Prepare') {
      steps {
        script {
          env.TAG = sh(returnStdout: true, script: 'git rev-parse --short=7 HEAD').trim()
        }
        echo "Building images tagged ${env.TAG}"
      }
    }

    stage('Build images') {
      parallel {
        stage('Backend') {
          steps {
            sh 'docker build -t $BACKEND_IMAGE:$TAG -t $BACKEND_IMAGE:latest backend'
          }
        }
        stage('Frontend') {
          steps {
            sh 'docker build -t $FRONTEND_IMAGE:$TAG -t $FRONTEND_IMAGE:latest frontend'
          }
        }
      }
    }

    stage('Push to Docker Hub') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
          sh '''
            echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin
            docker push $BACKEND_IMAGE:$TAG
            docker push $BACKEND_IMAGE:latest
            docker push $FRONTEND_IMAGE:$TAG
            docker push $FRONTEND_IMAGE:latest
            docker logout
          '''
        }
      }
    }
  }
}
