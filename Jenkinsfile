pipeline {
    agent none

    environment {
        VENV_DIR = "${WORKSPACE}\\venv"
        APP_NAME = "inventory-app"
        FAILED_STAGE = 'unknown'
    }

    stages {
        stage('Setup Environment') {
            agent any
            steps {
                script {
                    env.FAILED_STAGE = 'Setup Environment'
                }
                bat """
                "C:\\Program Files\\WindowsApps\\PythonSoftwareFoundation.Python.3.13_3.13.2544.0_x64__qbz5n2kfra8p0\\python.exe" -m venv "%VENV_DIR%"
                "%VENV_DIR%\\Scripts\\pip.exe" install --upgrade pip
                "%VENV_DIR%\\Scripts\\pip.exe" install -r requirements.txt
                """
            }
        }

        stage('Code Quality') {
            agent any
            steps {
                script {
                    env.FAILED_STAGE = 'Code Quality'
                    def scannerHome = tool 'SonarScanner'
                    withSonarQubeEnv('sonarqube-server') {
                        bat """
                        "${scannerHome}\\bin\\sonar-scanner"
                        """
                    }
                }
            }
        }

        stage('Quality Gate') {
            agent any
            steps {
                timeout(time: 3, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
                script {
                    env.FAILED_STAGE = 'Quality Gate'
                }
            }
        }

        stage('Setup Staging Database') {
            agent any
            steps {
                withCredentials([string(credentialsId: 'db-password', variable: 'DB_PASSWORD')]) {
                    bat """
                    mysql -u inventory_user -p%DB_PASSWORD% < db\\schema.sql
                    mysql -u inventory_user -p%DB_PASSWORD% < db\\seed.sql
                    """
                }
                script {
                    env.FAILED_STAGE = 'Setup Staging Database'
                }
            }
        }

        stage('End-to-End Playwright Tests') {
            agent any
            steps {
                script {
                    env.FAILED_STAGE = 'End-to-End Playwright Tests'
                }
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
            agent any
            steps {
                script {
                    env.FAILED_STAGE = 'Performance Test with k6'
                }
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
            agent any
            when {
                expression {
                    return env.BRANCH_NAME.endsWith('/main')
                }
            }
            steps {
                script {
                    env.FAILED_STAGE = 'Build Artifacts'
                }
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
            slackSend(
                channel: '#all-personal-workspace',
                color: 'good',
                tokenCredentialId: 'slack-webhook',
                message: "✅ Pipeline Succeeded\nJob: ${env.JOB_NAME}\nBuild: #${env.BUILD_NUMBER}\nBranch: ${env.BRANCH_NAME ?: 'unknown'}"
            )
        }
        failure {
            slackSend(
                channel: '#all-personal-workspace',
                color: 'danger',
                tokenCredentialId: 'slack-webhook',
                message: "❌ Pipeline Failed\nJob: ${env.JOB_NAME}\nBuild: #${env.BUILD_NUMBER}\nBranch: ${env.BRANCH_NAME ?: 'unknown'}\nFailed Stage: ${env.FAILED_STAGE}"
            )
        }
    }
}
