/**
 * Return the base URL for a given environment.
 *
 * Usage:
 *   def url = getEnvironmentUrl('staging')
 */

def call(String environment) {
    def urls = [
        'dev'       : 'https://transactbank-dev.internal.company.com',
        'staging'   : 'https://transactbank-staging.company.com',
        'production': 'https://api.transactbank.company.com',
    ]

    def url = urls[environment]
    if (!url) {
        error("Unknown environment: ${environment}. Valid: ${urls.keySet()}")
    }
    return url
}
