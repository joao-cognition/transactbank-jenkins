/**
 * Send a Slack notification with build status.
 *
 * Usage:
 *   notifySlack(
 *       channel: '#my-channel',
 *       status: 'SUCCESS',     // SUCCESS, FAILURE, UNSTABLE, ABORTED
 *       message: 'Build passed!',
 *   )
 */

def call(Map config = [:]) {
    def channel = config.channel ?: '#builds'
    def status  = config.status  ?: currentBuild.currentResult
    def message = config.message ?: "Build ${currentBuild.fullDisplayName} - ${status}"

    def colorMap = [
        'SUCCESS' : '#36a64f',
        'FAILURE' : '#cc0000',
        'UNSTABLE': '#ffcc00',
        'ABORTED' : '#808080',
    ]
    def color = colorMap[status] ?: '#439FE0'

    def emoji = [
        'SUCCESS' : ':white_check_mark:',
        'FAILURE' : ':x:',
        'UNSTABLE': ':warning:',
        'ABORTED' : ':no_entry:',
    ]

    def payload = """
    {
        "channel": "${channel}",
        "attachments": [
            {
                "color": "${color}",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "${emoji[status] ?: ':grey_question:'} ${message}"
                        }
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": "Job: *${env.JOB_NAME}* | Build: *#${env.BUILD_NUMBER}* | <${env.BUILD_URL}|View>"
                            }
                        ]
                    }
                ]
            }
        ]
    }
    """

    withCredentials([string(credentialsId: 'slack-webhook-url', variable: 'SLACK_WEBHOOK')]) {
        httpRequest(
            url: env.SLACK_WEBHOOK,
            httpMode: 'POST',
            contentType: 'APPLICATION_JSON',
            requestBody: payload,
            validResponseCodes: '200',
            quiet: true,
        )
    }
}
