pipeline {
    agent none

    environment {
        VENV_DIR = "${WORKSPACE}\\venv"
        APP_NAME = "inventory-app"
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
            agent { label 'build' }
            steps {
                bat """
                %VENV%\\Scripts\\python.exe setup.py sdist bdist_wheel
                dir dist
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
            echo "Pipeline completed successfully"
        }
        failure {
            echo "Pipeline failed"
        }
    }
}
