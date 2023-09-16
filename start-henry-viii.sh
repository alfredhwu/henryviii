#!/usr/bin/env bash
set -e
source ".venv/bin/activate"
waitress-serve --call henryviii:create_app
