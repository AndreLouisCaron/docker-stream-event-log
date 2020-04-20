#!/bin/sh

# Render `logrotate.conf` template given container environment variables.
cat /logrotate.tpl.conf | envsubst > /etc/logrotate.conf

# Configure `cron` to run `logrotate` at the desired schedule.
echo "$CRON_SCHEDULE /usr/sbin/logrotate -v -f /etc/logrotate.conf -s ${LOGROTATE_DB}" | crontab -

# Run `cron` via `tini` (https://github.com/krallin/tini).
exec tini $@
