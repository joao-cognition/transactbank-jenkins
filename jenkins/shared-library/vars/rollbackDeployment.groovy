/**
 * Rollback a Kubernetes deployment to the previous revision.
 *
 * Usage:
 *   rollbackDeployment(
 *       appName: 'my-app',
 *       environment: 'staging',
 *       namespace: 'my-namespace',
 *   )
 */

def call(Map config = [:]) {
    def appName     = config.appName     ?: error("appName is required")
    def environment = config.environment ?: error("environment is required")
    def namespace   = config.namespace   ?: appName

    echo "ROLLBACK: Rolling back ${appName} in ${environment}"

    withCredentials([
        file(credentialsId: "k8s-kubeconfig-${environment}", variable: 'KUBECONFIG')
    ]) {
        sh """
            echo "Current revision:"
            kubectl rollout history deployment/${appName} -n ${namespace} | tail -5

            echo "Rolling back..."
            kubectl rollout undo deployment/${appName} -n ${namespace}

            echo "Waiting for rollback to complete..."
            kubectl rollout status deployment/${appName} \
                -n ${namespace} \
                --timeout=300s

            echo "Rollback complete. Current revision:"
            kubectl rollout history deployment/${appName} -n ${namespace} | tail -5
        """
    }

    notifySlack(
        channel: '#transactbank-deploys',
        status: 'UNSTABLE',
        message: ":rewind: *${appName}* rolled back in *${environment}*. Investigate the failed deployment.",
    )
}
