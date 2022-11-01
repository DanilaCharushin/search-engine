#!/usr/bin/env sh

# This script runs locally from venv and in CI

PYTHON="${1:-python3}"

$PYTHON -m flake8 & flake_code=$!
$PYTHON -m black . --check & black_code=$!
$PYTHON -m isort . --check-only & isort_code=$!

wait $flake_code || code=$? || $code
wait $black_code || code=$? || $code
wait $isort_code || code=$? || $code
exit $code
