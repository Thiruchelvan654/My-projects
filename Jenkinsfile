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
    NAMESPACE      = 'fullstack-dev'
    KIND_NODE      = 'tf-lab-control-plane'
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

    stage('Security scan (Trivy)') {
      parallel {
        stage('Scan backend') {
          steps {
            sh '''
              docker run --rm \
                -v /var/run/docker.sock:/var/run/docker.sock \
                -v trivy-cache:/root/.cache/ \
                aquasec/trivy:latest image \
                --severity CRITICAL --exit-code 1 --ignore-unfixed --no-progress \
                $BACKEND_IMAGE:$TAG
            '''
          }
        }
        stage('Scan frontend') {
          steps {
            sh '''
              docker run --rm \
                -v /var/run/docker.sock:/var/run/docker.sock \
                -v trivy-cache:/root/.cache/ \
                aquasec/trivy:latest image \
                --severity CRITICAL --exit-code 1 --ignore-unfixed --no-progress \
                $FRONTEND_IMAGE:$TAG
            '''
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

    stage('Deploy to tf-lab') {
      steps {
        sh '''
          docker exec $KIND_NODE cat /etc/kubernetes/admin.conf > kubeconfig-tf-lab
          export KUBECONFIG=$PWD/kubeconfig-tf-lab
          kubectl set image deployment/backend-deployment backend=$BACKEND_IMAGE:$TAG -n $NAMESPACE
          kubectl set image deployment/frontend-deployment frontend=$FRONTEND_IMAGE:$TAG -n $NAMESPACE
          kubectl rollout status deployment/backend-deployment -n $NAMESPACE --timeout=180s
          kubectl rollout status deployment/frontend-deployment -n $NAMESPACE --timeout=180s
        '''
      }
      post {
        always {
          sh 'rm -f kubeconfig-tf-lab'
        }
      }
    }
  }
}
