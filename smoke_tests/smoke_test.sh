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
${ABSL_VIRTUALENV} --no-site-packages -p ${ABSL_PYTHON} ${TMP_DIR}

# Temporarily disable unbound variable errors to activate virtualenv.
set +u
if [[ $(uname -s) == MSYS* ]]; then
  source ${TMP_DIR}/scripts/activate
else
  source ${TMP_DIR}/bin/activate
fi
set -u

trap 'deactivate' EXIT

python setup.py install
python smoke_tests/smoke_test.py --echo smoke 2>&1 |grep 'echo is smoke.'
