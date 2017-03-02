#!/usr/bin/env bash
cd $(dirname "$0")
gunicorn yourss.wsgi