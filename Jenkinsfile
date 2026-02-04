pipeline {
    agent none
    def FAILED_STAGE = ''

    environment {
        VENV_DIR = "${WORKSPACE}\\venv"
        APP_NAME = "inventory-app"
        BRANCH = "${env.GIT_BRANCH ?: 'unknown'}"
        SONAR_SCANNER_HOME = tool 'SonarScanner'
    }

    stages {
        script {
            FAILED_STAGE = env.STAGE_NAME
        }
        stage('Setup Environment') {
            agent { label 'python' }
            steps {
                bat """
                "C:\\Program Files\\WindowsApps\\PythonSoftwareFoundation.Python.3.13_3.13.2544.0_x64__qbz5n2kfra8p0\\python.exe" -m venv "%VENV_DIR%"
                "%VENV_DIR%\\Scripts\\pip.exe" install --upgrade pip
                "%VENV_DIR%\\Scripts\\pip.exe" install -r requirements.txt
                """
            }
        }

        stage('Code Quality') {
            agent { label 'quality' }
            script {
                FAILED_STAGE = env.STAGE_NAME
            }
            steps {
                withSonarQubeEnv('SonarQube') {
                    bat """
                    "%SONAR_SCANNER_HOME%\\bin\\sonar-scanner.bat"
                    """
                }
            }
        }

        stage('Quality Gate') {
            script {
                FAILED_STAGE = env.STAGE_NAME
            }
            steps {
                timeout(time: 1, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Setup Staging Database') {
            script {
                FAILED_STAGE = env.STAGE_NAME
            }
            steps {
                withCredentials([string(credentialsId: 'db-password', variable: 'DB_PASSWORD')]) {
                    bat """
                    mysql -u inventory_user -p%DB_PASSWORD% < db\\schema.sql
                    mysql -u inventory_user -p%DB_PASSWORD% < db\\seed.sql
                    """
                }
            }
        }

        stage('End-to-End Playwright Tests') {
            script {
                FAILED_STAGE = env.STAGE_NAME
            }
            steps {
                bat """
                set PYTHONPATH=%WORKSPACE%
                "%VENV_DIR%\\Scripts\\pytest.exe" tests\\e2e --html=reports\\e2e-report.html --self-contained-html
                """
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/*.html'
                }
            }
        }

        stage('Performance Test with k6') {
            script {
                FAILED_STAGE = env.STAGE_NAME
            }
            steps {
                bat """
                k6 run --out json=reports\\k6-results.json tests\\performance\\load_test.js
                """
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/*.json'
                }
            }
        }


        stage('Build Artifacts') {
            when {
                expression {
                    return BRANCH.endsWith('/main')
                }
            }
            agent { label 'build' }
            script {
                FAILED_STAGE = env.STAGE_NAME
            }
            steps {
                bat """
                if not exist dist mkdir dist
                tar -czf dist\\%APP_NAME%-%BUILD_NUMBER%.tar.gz app requirements.txt db
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
            slackSend(
                message: "Jenkins pipeline succeeded.\n" +
                        "Job: ${env.JOB_NAME}\n" +
                        "Build: #${env.BUILD_NUMBER}\n" +
                        "Branch: ${BRANCH}"
            )
        }
        failure {
            echo "Pipeline failed on ${BRANCH}"
            slackSend(
                message: "Jenkins pipeline failed.\n" +
                        "Job: ${env.JOB_NAME}\n" +
                        "Build: #${env.BUILD_NUMBER}\n" +
                        "Branch: ${BRANCH}\n" +
                        "Failed Stage: ${FAILED_STAGE}"
            )
        }
    }
}
