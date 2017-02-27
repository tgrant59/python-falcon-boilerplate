from app.async import mailer


def report_error(error):
    mailer.error(error)
