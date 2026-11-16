#!/usr/bin/env bash
set -euo pipefail
cat \
  data_bundle.tar.xz.part00 \
  data_bundle.tar.xz.part01 \
  data_bundle.tar.xz.part02 \
  data_bundle.tar.xz.part03 \
  > data_bundle.tar.xz
echo "52bf2a5c23197fa312da2ce2b9da723f185275a230511bd7939b85672443cecb  data_bundle.tar.xz" | sha256sum -c -
tar -tJf data_bundle.tar.xz
