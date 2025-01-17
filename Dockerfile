FROM python:3.13.1-slim-bookworm

WORKDIR /app

ARG UID=1000
ARG GID=1000


RUN set -eu;\
	groupadd -g "${GID}" python;\
	useradd --create-home --no-log-init -u "${UID}" -g "${GID}" python
	#chown python:python -R /app

COPY --chown=python:python . .

RUN pip install -r requirements.txt

#USER python
EXPOSE 8000


ENV YOURSS_DEBUG=false
ENV YOURSS_BASE_URL=yourss.legeyda.com
ENV YOURSS_LOG_LEVEL=info
CMD ["gunicorn", "--bind=0.0.0.0:8000", "yourss.wsgi"]