import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .report import (Report, PlainReportPrinter, HTMLReportPrinter)


def sendmail(report: Report):
    host = os.environ['SMTP_HOST']
    port = 465
    user = os.environ['SMTP_USER']
    from_name = os.environ['SMTP_FROM_NAME']
    from_address = os.environ['SMTP_FROM_ADDRESS']
    to_addrs = os.environ['SMTP_TO_ADDRESS'].split(',')
    password = os.environ['SMTP_PASSWORD']

    msg = MIMEMultipart('alternative')
    msg['Subject'] = report.header
    msg['From'] = f'{from_name} <{from_address}>'

    msg.attach(MIMEText(PlainReportPrinter(report).print(), 'plain'))
    msg.attach(MIMEText(HTMLReportPrinter(report).print(), 'html', 'utf-8'))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(host, port, context=context, timeout=120) as server:
        server.login(user, password)
        return server.sendmail(from_address, to_addrs, msg.as_string())
