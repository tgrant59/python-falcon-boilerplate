FROM alpine:3.4
MAINTAINER Tom Grant <t.grant@outlook.com>

RUN apk update --no-cache
RUN apk add --update --no-cache \
    mysql \
    mysql-client \
    pwgen

COPY init-mysql.sh init-mysql.sh

EXPOSE 3306
VOLUME ["/var/lib/mysql"]

CMD /bin/sh init-mysql.sh
