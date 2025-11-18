# Notification Worker

## Overview
Handles outbound notifications such as webhooks, emails, or Slack messages.

## Responsibilities
- Listen for system events
- Format human-readable messages
- Deliver notifications to channels

## Consumes Events
- `document.processed`
- `query.ready`
- `error.occurred`
- Any other system event

## Produces Events
- none (usually)

## Running Locally

task dev
poetry run python src/main.py


## Environment Variables

SLACK_WEBHOOK_URL=
EMAIL_SMTP_SERVER=
RABBITMQ_URL=


## Testing

pytest


## Extending
Add new notification channels or templates.
