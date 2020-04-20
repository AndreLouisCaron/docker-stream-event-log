# -*- coding: utf-8 -*-

FROM alpine:3.7

ENV CRON_SCHEDULE='0 * * * *'

RUN apk --no-cache add logrotate tini gettext libintl \
    && mkdir -p /logs \
    && mkdir -p /etc/logrotate.d

COPY logrotate.tpl.conf /logrotate.tpl.conf

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
RUN mkdir -p /var/run/logrotate/
ENV LOGROTATE_DB=/var/run/logrotate/logrotate.db

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

CMD ["/usr/sbin/crond", "-f", "-L", "/dev/stdout"]
