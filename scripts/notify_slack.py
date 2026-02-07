#!/usr/bin/env python3
"""
Send rule violation reports to Slack via webhook.
Category: automation
"""
import os
import sys
import smtplib
import requests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser

parser = get_arg_parser()
args = parser.parse_args()
logger = get_logger(debug=args.debug)
def send_slack_notification(message, webhook_url=None):
    """
    Send a message to Slack via webhook.
    Args:
        message (str): The message to send.
        webhook_url (str): Slack webhook URL. If None, uses SLACK_WEBHOOK_URL env var.
    """
    if webhook_url is None:
        webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook_url:
        logger.error("SLACK_WEBHOOK_URL not set.")
        return False
    payload = {"text": message}
    resp = requests.post(webhook_url, json=payload)
    if resp.status_code != 200:
        logger.error(f"Failed to send Slack notification: {resp.text}")
        return False
    logger.info("Slack notification sent.")
    return True

def main():
    try:
        webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
        if not webhook_url:
            logger.error("SLACK_WEBHOOK_URL not set.")
            sys.exit(1)
        message = sys.stdin.read()
        payload = {"text": message}
        resp = requests.post(webhook_url, json=payload)
        if resp.status_code != 200:
            logger.error(f"Failed to send Slack notification: {resp.text}")
        else:
            logger.info("Slack notification sent.")
    except Exception as e:
        logger.error(f"Exception in notify_slack: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
