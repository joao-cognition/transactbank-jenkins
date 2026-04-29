/**
 * Execute a closure inside an activated Python virtual environment.
 *
 * Usage:
 *   withPythonVenv {
 *       sh 'pytest tests/'
 *   }
 */

def call(Map config = [:], Closure body) {
    def venvDir = config.venvDir ?: "${env.WORKSPACE}/.venv"
    def pythonVersion = config.pythonVersion ?: '3.11'

    sh """
        python${pythonVersion} -m venv ${venvDir} || python3 -m venv ${venvDir}
        . ${venvDir}/bin/activate
        pip install --upgrade pip setuptools wheel
    """

    withEnv(["PATH=${venvDir}/bin:${env.PATH}", "VIRTUAL_ENV=${venvDir}"]) {
        body()
    }
}
