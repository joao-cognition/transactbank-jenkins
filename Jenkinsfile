/**
 * TransactBank API — Main CI Pipeline
 *
 * Triggered on every push to any branch and on pull requests.
 * Stages: Checkout → Install → Lint → Unit Tests → Integration Tests →
 *         SonarQube → Security Scan → Docker Build → Deploy (branch-gated)
 *
 * Required Jenkins plugins:
 *   - Pipeline, Pipeline Utility Steps
 *   - Docker Pipeline, Docker Workflow
 *   - SonarQube Scanner
 *   - Slack Notification
 *   - Credentials Binding
 *   - JUnit, Cobertura
 *   - HTML Publisher
 *   - Warnings Next Generation
 */

@Library('transactbank-shared-lib') _

pipeline {
    agent {
        docker {
            image 'python:3.11-slim'
            args '-v /var/run/docker.sock:/var/run/docker.sock --network host'
            label 'docker-agent'
        }
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20', artifactNumToKeepStr: '5'))
        timestamps()
        ansiColor('xterm')
        retry(1)
    }

    environment {
        APP_NAME        = 'transactbank-api'
        PYTHON_VERSION  = '3.11'
        VENV_DIR        = "${WORKSPACE}/.venv"
        PATH            = "${VENV_DIR}/bin:${PATH}"
        DOCKER_REGISTRY = credentials('docker-registry-url')
        DOCKER_CREDS    = credentials('docker-registry-credentials')
        SONAR_TOKEN     = credentials('sonarqube-token')
        SONAR_HOST      = credentials('sonarqube-host-url')
        SLACK_CHANNEL   = '#transactbank-ci'
        DATABASE_URL    = "sqlite:///${WORKSPACE}/test.db"
        FLASK_ENV       = 'testing'
    }

    parameters {
        choice(
            name: 'DEPLOY_ENV',
            choices: ['none', 'dev', 'staging'],
            description: 'Target deployment environment (prod requires Jenkinsfile.release)'
        )
        booleanParam(
            name: 'SKIP_SONAR',
            defaultValue: false,
            description: 'Skip SonarQube analysis'
        )
        booleanParam(
            name: 'FORCE_DOCKER_BUILD',
            defaultValue: false,
            description: 'Build Docker image even on feature branches'
        )
        string(
            name: 'DOCKER_TAG_OVERRIDE',
            defaultValue: '',
            description: 'Override Docker image tag (default: branch-commit)'
        )
    }

    triggers {
        pollSCM('H/5 * * * *')
        githubPush()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.GIT_COMMIT_SHORT = sh(
                        script: 'git rev-parse --short HEAD',
                        returnStdout: true
                    ).trim()
                    env.GIT_BRANCH_CLEAN = env.BRANCH_NAME?.replaceAll('/', '-') ?: 'unknown'
                    env.DOCKER_TAG = params.DOCKER_TAG_OVERRIDE ?: "${env.GIT_BRANCH_CLEAN}-${env.GIT_COMMIT_SHORT}"

                    echo "Building ${APP_NAME} @ ${env.GIT_COMMIT_SHORT} on ${env.GIT_BRANCH_CLEAN}"
                }
            }
        }

        stage('Setup Python Environment') {
            steps {
                sh '''
                    python -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip setuptools wheel
                    pip install -r requirements.txt
                    pip install -r requirements-dev.txt
                '''
            }
        }

        stage('Quality Checks') {
            parallel {
                stage('Lint — flake8') {
                    steps {
                        sh '''
                            . ${VENV_DIR}/bin/activate
                            flake8 app/ tests/ \
                                --format=pylint \
                                --output-file=reports/flake8-report.txt \
                                --statistics \
                                --count || true
                        '''
                        recordIssues(
                            tools: [flake8(pattern: 'reports/flake8-report.txt')],
                            qualityGates: [[threshold: 10, type: 'TOTAL', unstable: true]]
                        )
                    }
                }

                stage('Lint — pylint') {
                    steps {
                        sh '''
                            . ${VENV_DIR}/bin/activate
                            mkdir -p reports
                            pylint app/ \
                                --output-format=parseable \
                                --reports=yes \
                                --rcfile=.pylintrc \
                                > reports/pylint-report.txt || true
                        '''
                        recordIssues(
                            tools: [pyLint(pattern: 'reports/pylint-report.txt')],
                            qualityGates: [[threshold: 20, type: 'TOTAL', unstable: true]]
                        )
                    }
                }

                stage('Type Check — mypy') {
                    steps {
                        sh '''
                            . ${VENV_DIR}/bin/activate
                            mypy app/ \
                                --ignore-missing-imports \
                                --html-report reports/mypy \
                                || true
                        '''
                        publishHTML(target: [
                            reportDir: 'reports/mypy',
                            reportFiles: 'index.html',
                            reportName: 'mypy Type Check Report',
                            keepAll: true,
                            alwaysLinkToLastBuild: true,
                        ])
                    }
                }

                stage('Security — Bandit') {
                    steps {
                        sh '''
                            . ${VENV_DIR}/bin/activate
                            bandit -r app/ \
                                -f json \
                                -o reports/bandit-report.json \
                                --severity-level medium \
                                || true
                        '''
                        archiveArtifacts artifacts: 'reports/bandit-report.json', allowEmptyArchive: true
                    }
                }
            }
        }

        stage('Unit Tests') {
            steps {
                sh '''
                    . ${VENV_DIR}/bin/activate
                    mkdir -p reports
                    pytest tests/unit/ \
                        -v \
                        --tb=short \
                        --junitxml=reports/unit-test-results.xml \
                        --cov=app \
                        --cov-report=xml:reports/coverage.xml \
                        --cov-report=html:reports/coverage-html \
                        --cov-fail-under=75
                '''
            }
            post {
                always {
                    junit 'reports/unit-test-results.xml'
                    cobertura(
                        coberturaReportFile: 'reports/coverage.xml',
                        conditionalCoverageTargets: '70, 0, 0',
                        lineCoverageTargets: '75, 0, 0',
                    )
                    publishHTML(target: [
                        reportDir: 'reports/coverage-html',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report',
                        keepAll: true,
                    ])
                }
            }
        }

        stage('Integration Tests') {
            steps {
                sh '''
                    . ${VENV_DIR}/bin/activate
                    pytest tests/integration/ \
                        -v \
                        --tb=short \
                        --junitxml=reports/integration-test-results.xml
                '''
            }
            post {
                always {
                    junit 'reports/integration-test-results.xml'
                }
            }
        }

        stage('SonarQube Analysis') {
            when {
                expression { return !params.SKIP_SONAR }
            }
            steps {
                withSonarQubeEnv('SonarQube-Server') {
                    sh '''
                        sonar-scanner \
                            -Dsonar.projectKey=transactbank-api \
                            -Dsonar.projectName="TransactBank API" \
                            -Dsonar.projectVersion=${DOCKER_TAG} \
                            -Dsonar.sources=app/ \
                            -Dsonar.tests=tests/ \
                            -Dsonar.python.coverage.reportPaths=reports/coverage.xml \
                            -Dsonar.python.flake8.reportPaths=reports/flake8-report.txt \
                            -Dsonar.python.pylint.reportPaths=reports/pylint-report.txt \
                            -Dsonar.host.url=${SONAR_HOST} \
                            -Dsonar.login=${SONAR_TOKEN}
                    '''
                }
            }
        }

        stage('SonarQube Quality Gate') {
            when {
                expression { return !params.SKIP_SONAR }
            }
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Docker Build & Push') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                    branch pattern: 'release/*', comparator: 'GLOB'
                    expression { return params.FORCE_DOCKER_BUILD }
                }
            }
            steps {
                script {
                    docker.withRegistry("https://${DOCKER_REGISTRY}", 'docker-registry-credentials') {
                        def image = docker.build(
                            "${DOCKER_REGISTRY}/${APP_NAME}:${DOCKER_TAG}",
                            "--build-arg PYTHON_VERSION=${PYTHON_VERSION} " +
                            "--build-arg BUILD_DATE=\$(date -u +'%Y-%m-%dT%H:%M:%SZ') " +
                            "--build-arg VCS_REF=${env.GIT_COMMIT_SHORT} " +
                            "--label org.opencontainers.image.revision=${env.GIT_COMMIT_SHORT} " +
                            "-f Dockerfile ."
                        )
                        image.push()
                        image.push('latest')
                    }
                }
            }
        }

        stage('Trivy Security Scan') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            steps {
                sh """
                    trivy image \
                        --exit-code 1 \
                        --severity HIGH,CRITICAL \
                        --format json \
                        --output reports/trivy-report.json \
                        ${DOCKER_REGISTRY}/${APP_NAME}:${DOCKER_TAG} \
                        || true
                """
                archiveArtifacts artifacts: 'reports/trivy-report.json', allowEmptyArchive: true
            }
        }

        stage('Deploy') {
            when {
                anyOf {
                    expression { return params.DEPLOY_ENV in ['dev', 'staging'] }
                    allOf {
                        branch 'develop'
                        expression { return params.DEPLOY_ENV == 'none' }
                    }
                }
            }
            steps {
                script {
                    def targetEnv = params.DEPLOY_ENV != 'none' ? params.DEPLOY_ENV : 'dev'
                    deployToEnvironment(
                        appName: APP_NAME,
                        imageTag: DOCKER_TAG,
                        environment: targetEnv,
                        registryUrl: DOCKER_REGISTRY,
                    )
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
            cleanWs()
        }
        success {
            notifySlack(
                channel: env.SLACK_CHANNEL,
                status: 'SUCCESS',
                message: "Build *${APP_NAME}* `${DOCKER_TAG}` passed all checks.",
            )
        }
        failure {
            notifySlack(
                channel: env.SLACK_CHANNEL,
                status: 'FAILURE',
                message: "Build *${APP_NAME}* `${DOCKER_TAG}` FAILED. <${BUILD_URL}|View logs>",
            )
        }
        unstable {
            notifySlack(
                channel: env.SLACK_CHANNEL,
                status: 'UNSTABLE',
                message: "Build *${APP_NAME}* `${DOCKER_TAG}` is UNSTABLE (quality warnings).",
            )
        }
    }
}
