pipeline {
    agent none

    environment {
        VENV_DIR = "${WORKSPACE}\\venv"
        APP_NAME = "inventory-app"
        BRANCH = "${env.GIT_BRANCH ?: 'unknown'}"
    }

    stages {
        stage('Setup Environment') {
            agent { label 'python' }
            steps {
                bat """
                "C:\\Program Files\\WindowsApps\\PythonSoftwareFoundation.Python.3.13_3.13.2544.0_x64__qbz5n2kfra8p0\\python.exe" -m venv %VENV%
                %VENV%\\Scripts\\pip.exe install --upgrade pip
                %VENV%\\Scripts\\pip.exe install -r requirements.txt
                """
            }
        }

        stage('Code Quality') {
            agent { label 'quality' }
            steps {
                bat '''
                    source ${VENV_DIR}/Scripts/activate
                    echo "Code quality placeholder"
                    echo "Branch: ${BRANCH}"
                '''
            }
        }

        stage('Run Tests') {
            steps {
                bat """
                set PYTHONPATH=%WORKSPACE%
                %VENV%\\Scripts\\pytest.exe --cov=app --cov-report=xml --junitxml=tests/results.xml --cov-fail-under=80
                """
            }
        }

        stage('Build Artifacts') {
            when {
                expression {
                    return BRANCH.endsWith('/main')
                }
            }
            agent { label 'build' }
            steps {
                bat """
                mkdir -p dist
                tar -czf dist/${APP_NAME}-${BUILD_NUMBER}.tar.gz app/ requirements.txt db/
                """
            }
            post {
                success {
                    archiveArtifacts artifacts: 'dist/*.tar.gz', fingerprint: true
                }
            }
        }
    }

    post {
        success {
            echo "Pipeline completed successfully on ${BRANCH}"
        }
        failure {
            echo "Pipeline failed on ${BRANCH}"
        }
    }
}
