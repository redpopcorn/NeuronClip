#!/usr/bin/env sh

python -m clipneuron.cli \
  --input "$1" \
  --output "$2" \
  --render \
  --top "${3:-5}" \
  --clips-dir "${4:-out/clips}"
