#!/bin/bash
# Copyright 2017 The Abseil Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Smoke test to verify setup.py works as expected.
# Note on Windows, this must run via msys.

# Fail on any error. Treat unset variables an error. Print commands as executed.
set -eux

if [[ "$#" -ne "2" ]]; then
  echo 'Must specify the Python interpreter and virtualenv path.'
  echo 'Usage:'
  echo '  smoke_tests/smoke_test.sh [Python interpreter path] [virtualenv Path]'
  exit 1
fi

ABSL_PYTHON=$1
ABSL_VIRTUALENV=$2
TMP_DIR=$(mktemp -d)
trap "{ rm -rf ${TMP_DIR}; }" EXIT
# Do not bootstrap pip/setuptools, they are manually installed with get-pip.py
# inside the virtualenv.
if ${ABSL_VIRTUALENV} --help | grep '\--no-site-packages'; then
  no_site_packages_flag="--no-site-packages"
else
  # --no-site-packages becomes the default in version 20 and is no longer a
  # flag.
  no_site_packages_flag=""
fi
${ABSL_VIRTUALENV} ${no_site_packages_flag} --no-pip --no-setuptools --no-wheel \
    -p ${ABSL_PYTHON} ${TMP_DIR}

# Temporarily disable unbound variable errors to activate virtualenv.
set +u
if [[ $(uname -s) == MSYS* ]]; then
  source ${TMP_DIR}/Scripts/activate
else
  source ${TMP_DIR}/bin/activate
fi
set -u

trap 'deactivate' EXIT

# When running macOS <= 10.12, pip 9.0.3 is required to connect to PyPI.
# So we need to manually use the latest pip to install absl-py. See:
# https://mail.python.org/pipermail/distutils-sig/2018-April/032114.html
if [[ "$(python -c "import sys; print(sys.version_info.major, sys.version_info.minor)")" == "3 6" ]]; then
  # Latest get-pip.py no longer supports Python 3.6.
  curl https://bootstrap.pypa.io/pip/3.6/get-pip.py | python
else
  curl https://bootstrap.pypa.io/get-pip.py | python
fi
pip --version

python --version
python setup.py install
python smoke_tests/sample_app.py --echo smoke 2>&1 |grep 'echo is smoke.'
python smoke_tests/sample_test.py 2>&1 | grep 'msg_for_test'
