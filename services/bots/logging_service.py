import logging


# ======================
# DISCORD GATEWAY FILTER
# ======================
class IgnoreGatewayResume(logging.Filter):

    def filter(
        self,
        record: logging.LogRecord
    ) -> bool:

        return (
            "has successfully RESUMED session"
            not in record.getMessage()
        )


# ======================
# ASYNCMY VALUES FILTER
# ======================
class IgnoreAsyncMyValuesWarning(logging.Filter):

    def filter(
        self,
        record: logging.LogRecord
    ) -> bool:

        return "VALUES function" not in record.getMessage()


# ======================
# SETUP LOG FILTER
# ======================
def setup_log_filters(
    production: bool,
    development: bool
):
    
    if production:

        logging.getLogger(
            "discord.gateway"
        ).addFilter(
            IgnoreGatewayResume()
        )

    if development:

        logging.getLogger(
            "asyncmy"
        ).addFilter(
            IgnoreAsyncMyValuesWarning()
        )