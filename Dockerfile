FROM node:10.15.3-alpine AS frontdependencies
ADD /ftl/frontend/package*.json /app/
WORKDIR /app
RUN npm ci



FROM frontdependencies AS frontbuild
COPY /ftl/frontend /app
WORKDIR /app
RUN npm run build


FROM python:3.7.4-slim
# PORT is used by uwsgi config, it's mainly used by Heroku because they assign random port to app.
ENV PORT 8000

# Workaround for https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=863199
RUN mkdir -p /usr/share/man/man1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gettext \
    openjdk-11-jre-headless \
    build-essential \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

ADD ftl/requirements.txt /app/requirements.txt
ADD docker/requirements_deploy.txt /app/requirements_deploy.txt
ADD docker/ftl_uwsgi.ini /app/ftl_uwsgi.ini
ADD docker/settings_local.py /app/ftl/settings_local.py

RUN python3 -m pip install -r /app/requirements.txt --no-cache-dir && \
 python3 -m pip install -r /app/requirements_deploy.txt --no-cache-dir

RUN apt-get remove --purge -y build-essential
RUN apt-get autoremove -y

# Run the image as a non-root user
RUN groupadd --gid 1000 ftl \
    && useradd --uid 1000 --gid ftl --shell /bin/bash --create-home ftl

# Those RUN true commands are a workaround for https://github.com/moby/moby/issues/37965
ADD --chown=ftl:ftl ftl /app/

COPY --chown=ftl:ftl --from=frontbuild /app/dist /app/frontend/dist
RUN true
COPY --chown=ftl:ftl --from=frontbuild /app/pdfjs /app/frontend/pdfjs
RUN true
COPY --chown=ftl:ftl --from=frontbuild /app/webpack-stats.json /app/frontend/
RUN true
COPY --chown=ftl:ftl --from=frontbuild /app/__init__.py /app/frontend/
RUN true

WORKDIR /app

RUN python3 -m compileall ./
RUN python3 manage.py compilemessages
RUN python3 manage.py collectstatic --no-input

ENV FTLDATA /app/uploads
RUN mkdir -p "$FTLDATA" && chown -R ftl:ftl "$FTLDATA" && chmod 777 "$FTLDATA"
VOLUME /app/uploads

# For local or standard use, must match the env var PORT value.
EXPOSE 8000
USER ftl
CMD uwsgi --ini /app/ftl_uwsgi.ini