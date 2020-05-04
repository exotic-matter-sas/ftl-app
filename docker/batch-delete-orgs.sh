#!/usr/bin/env sh

if [ -z "$CRON_DISABLE" ]; then
  curl -H "X-Appengine-Cron: true" http://localhost:$PORT/crons-account/$CRON_SECRET_KEY/batch-delete-orgs
  touch /tmp/batch-delete-orgs-last-run
fi
