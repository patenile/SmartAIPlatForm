#!/usr/bin/env python3
"""
Send rule violation reports to email via SMTP.
Category: automation
"""
import os
import sys
import smtplib
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from email.message import EmailMessage
from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser

parser = get_arg_parser()
args = parser.parse_args()
logger = get_logger(debug=args.debug)
def send_email_notification(subject, body, to_email=None):
    """Minimal stub for import compatibility. Sends an email notification if environment is set."""
    smtp_server = os.environ.get("SMTP_SERVER")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASS")
    notify_email = to_email or os.environ.get("NOTIFY_EMAIL")
    if not (smtp_server and smtp_user and smtp_pass and notify_email):
        logger.error("SMTP_SERVER, SMTP_USER, SMTP_PASS, and NOTIFY_EMAIL must be set.")
        logger.error("Missing environment variables. Please set SMTP_SERVER, SMTP_USER, SMTP_PASS, and NOTIFY_EMAIL in your .env file or environment.")
        logger.error("See docs/email_setup.md for details.")
        return False
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = notify_email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        logger.info("Email notification sent.")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False

def main():
    logger = get_logger(debug=args.debug)
    try:
        smtp_server = os.environ.get("SMTP_SERVER")
        smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        smtp_user = os.environ.get("SMTP_USER")
        smtp_pass = os.environ.get("SMTP_PASS")
        to_email = os.environ.get("NOTIFY_EMAIL")
        if not (smtp_server and smtp_user and smtp_pass and to_email):
            logger.error("SMTP_SERVER, SMTP_USER, SMTP_PASS, and NOTIFY_EMAIL must be set.")
            logger.error("Missing environment variables. Please set SMTP_SERVER, SMTP_USER, SMTP_PASS, and NOTIFY_EMAIL in your .env file or environment.")
            logger.error("See docs/email_setup.md for details.")
            sys.exit(1)
        message = sys.stdin.read()
        msg = EmailMessage()
        msg.set_content(message)
        msg["Subject"] = "SmartAIPlatform Rule Violation Report"
        msg["From"] = smtp_user
        msg["To"] = to_email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        logger.info("Email notification sent.")
    except Exception as e:
        logger.error(f"Exception in notify_email: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
