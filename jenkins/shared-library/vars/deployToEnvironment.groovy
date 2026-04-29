/**
 * Deploy a Docker image to a target Kubernetes environment.
 *
 * Usage:
 *   deployToEnvironment(
 *       appName: 'my-app',
 *       imageTag: 'main-abc1234',
 *       environment: 'staging',
 *       registryUrl: 'registry.company.com',
 *   )
 */

def call(Map config = [:]) {
    def appName     = config.appName     ?: error("appName is required")
    def imageTag    = config.imageTag    ?: error("imageTag is required")
    def environment = config.environment ?: error("environment is required")
    def registryUrl = config.registryUrl ?: error("registryUrl is required")
    def namespace   = config.namespace   ?: appName
    def replicas    = config.replicas    ?: getDefaultReplicas(environment)

    echo "Deploying ${appName}:${imageTag} to ${environment} (${replicas} replicas)"

    withCredentials([
        file(credentialsId: "k8s-kubeconfig-${environment}", variable: 'KUBECONFIG')
    ]) {
        // Apply Kubernetes manifests with variable substitution
        sh """
            export IMAGE_TAG=${imageTag}
            export REGISTRY_URL=${registryUrl}
            export APP_NAME=${appName}
            export REPLICAS=${replicas}
            export ENVIRONMENT=${environment}

            envsubst < kubernetes/deployment.yaml | kubectl apply -f - -n ${namespace}
            envsubst < kubernetes/service.yaml    | kubectl apply -f - -n ${namespace}
            envsubst < kubernetes/configmap.yaml  | kubectl apply -f - -n ${namespace}

            kubectl rollout status deployment/${appName} \
                -n ${namespace} \
                --timeout=300s
        """
    }

    // Verify deployment health
    sh """
        MAX_RETRIES=10
        RETRY_INTERVAL=5
        for i in \$(seq 1 \$MAX_RETRIES); do
            HEALTH=\$(kubectl exec -n ${namespace} \
                deploy/${appName} -- \
                curl -sf http://localhost:5000/health 2>/dev/null || true)
            if echo "\$HEALTH" | grep -q healthy; then
                echo "Deployment verified healthy after \$i attempts"
                exit 0
            fi
            echo "Attempt \$i/\$MAX_RETRIES — waiting..."
            sleep \$RETRY_INTERVAL
        done
        echo "ERROR: Deployment health check failed after \$MAX_RETRIES attempts"
        exit 1
    """
}

private int getDefaultReplicas(String environment) {
    switch (environment) {
        case 'dev':        return 1
        case 'staging':    return 2
        case 'production': return 3
        default:           return 1
    }
}
