pipeline {
    agent none

    environment {
        VENV_DIR = "${WORKSPACE}\\venv"
        APP_NAME = "inventory-app"
        BRANCH = "${env.GIT_BRANCH ?: 'unknown'}"
        SONAR_SCANNER_HOME = tool 'SonarScanner'
        FAILED_STAGE = ''
    }

    stages {
        stage('Setup Environment') {
            agent { label 'python' }
            steps {
                script {
                    env.FAILED_STAGE = env.STAGE_NAME
                }
                bat """
                "C:\\Program Files\\WindowsApps\\PythonSoftwareFoundation.Python.3.13_3.13.2544.0_x64__qbz5n2kfra8p0\\python.exe" -m venv "%VENV_DIR%"
                "%VENV_DIR%\\Scripts\\pip.exe" install --upgrade pip
                "%VENV_DIR%\\Scripts\\pip.exe" install -r requirements.txt
                """
            }
        }

        stage('Code Quality') {
            agent { label 'quality' }
            steps {
                script {
                    env.FAILED_STAGE = env.STAGE_NAME
                }
                withSonarQubeEnv('SonarQube') {
                    bat """
                    "%SONAR_SCANNER_HOME%\\bin\\sonar-scanner.bat"
                    """
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 1, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
                script {
                    env.FAILED_STAGE = env.STAGE_NAME
                }
            }
        }

        stage('Setup Staging Database') {
            steps {
                withCredentials([string(credentialsId: 'db-password', variable: 'DB_PASSWORD')]) {
                    bat """
                    mysql -u inventory_user -p%DB_PASSWORD% < db\\schema.sql
                    mysql -u inventory_user -p%DB_PASSWORD% < db\\seed.sql
                    """
                }
                script {
                    env.FAILED_STAGE = env.STAGE_NAME
                }
            }
        }

        stage('End-to-End Playwright Tests') {
            steps {
                script {
                    env.FAILED_STAGE = env.STAGE_NAME
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
            steps {
                script {
                    env.FAILED_STAGE = env.STAGE_NAME
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
            when {
                expression {
                    return BRANCH.endsWith('/main')
                }
            }
            agent { label 'build' }
            steps {
                script {
                    env.FAILED_STAGE = env.STAGE_NAME
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
            echo "Pipeline completed successfully on ${env.BRANCH}"
            slackSend(
                message: "Jenkins pipeline succeeded.\n" +
                        "Job: ${env.JOB_NAME}\n" +
                        "Build: #${env.BUILD_NUMBER}\n" +
                        "Branch: ${env.BRANCH}"
            )
        }
        failure {
            echo "Pipeline failed on ${env.BRANCH}"
            slackSend(
                message: "Jenkins pipeline failed.\n" +
                        "Job: ${env.JOB_NAME}\n" +
                        "Build: #${env.BUILD_NUMBER}\n" +
                        "Branch: ${env.BRANCH}\n" +
                        "Failed Stage: ${env.FAILED_STAGE}"
            )
        }
    }
}
