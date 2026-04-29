# Jenkins Credentials Reference

This document lists all credentials required in Jenkins for the CI/CD pipelines to function.

## Required Credentials

| Credential ID                      | Type              | Used In              | Description                                      |
|------------------------------------|-------------------|----------------------|--------------------------------------------------|
| `docker-registry-url`             | Secret text       | Jenkinsfile, CD      | Docker registry hostname (e.g., `ecr.aws/...`)  |
| `docker-registry-credentials`     | Username/Password | Jenkinsfile, CD      | Registry login credentials                       |
| `sonarqube-token`                 | Secret text       | Jenkinsfile          | SonarQube authentication token                   |
| `sonarqube-host-url`              | Secret text       | Jenkinsfile          | SonarQube server URL                             |
| `slack-webhook-url`               | Secret text       | All pipelines        | Slack incoming webhook URL                       |
| `k8s-kubeconfig-dev`              | Secret file       | CD                   | Kubernetes config for dev cluster                |
| `k8s-kubeconfig-staging`          | Secret file       | CD                   | Kubernetes config for staging cluster            |
| `k8s-kubeconfig-production`       | Secret file       | CD                   | Kubernetes config for production cluster         |
| `db-url-staging`                  | Secret text       | CD                   | PostgreSQL connection string for staging         |
| `db-url-production`               | Secret text       | CD                   | PostgreSQL connection string for production      |
| `github-deploy-key`               | SSH key           | Release              | GitHub deploy key for pushing tags               |
| `github-token`                    | Secret text       | Release              | GitHub PAT for creating releases                 |
| `datadog-api-key`                 | Secret text       | CD                   | Datadog API key for deployment events            |

## Jenkins Plugins Required

- Pipeline
- Pipeline Utility Steps
- Docker Pipeline / Docker Workflow
- SonarQube Scanner
- Slack Notification
- Credentials Binding
- JUnit
- Cobertura
- HTML Publisher
- Warnings Next Generation (for flake8/pylint)
- OWASP Dependency Check
- SSH Agent
- HTTP Request
- AnsiColor
- Timestamper
