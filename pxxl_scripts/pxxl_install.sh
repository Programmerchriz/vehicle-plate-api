#!/usr/bin/env sh

set -eu

WHEELHOUSE=".pxxl-wheelhouse"

mkdir -p "$WHEELHOUSE"

python -m pip install --upgrade pip setuptools wheel

if ! find "$WHEELHOUSE" \
  -name "opencv_python_headless-4.11.0.86-*.whl" \
  -print \
  -quit \
  | grep -q .; then
  echo "Building OpenCV wheel..."

  python -m pip wheel \
    --wheel-dir "$WHEELHOUSE" \
    --no-deps \
    opencv-python-headless==4.11.0.86
else
  echo "Using cached OpenCV wheel."
fi

python -m pip install \
  --prefer-binary \
  --find-links="$WHEELHOUSE" \
  -r requirements.txt

python -m pip install \
  --no-deps \
  ultralytics==8.4.93 \
  easyocr==1.7.2