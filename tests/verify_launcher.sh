#!/bin/bash
set -e
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
python tests/verify_launcher.py
