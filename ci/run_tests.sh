#!/bin/bash

# Fail on any error. Treat unset variables an error. Print commands as executed.
set -eux

# Log environment variables.
env

# Let the script continue even if "bazel test" fails, so that all tests are
# always executed.
exit_code=0

# Log the bazel version for easier debugging.
bazel version
bazel test --test_output=errors absl/... || exit_code=$?
if [[ ! -z "${ABSL_EXPECTED_PYTHON_VERSION}" ]]; then
    bazel test \
        --test_output=errors absl:tests/python_version_test \
        --test_arg=--expected_version="${ABSL_EXPECTED_PYTHON_VERSION}" || exit_code=$?
fi

if [[ ! -z "${ABSL_COPY_TESTLOGS_TO}" ]]; then
    mkdir -p "${ABSL_COPY_TESTLOGS_TO}"
    readonly testlogs_dir=$(bazel info bazel-testlogs)
    echo "Copying bazel test logs from ${testlogs_dir} to ${ABSL_COPY_TESTLOGS_TO}..."
    cp -r "${testlogs_dir}" "${ABSL_COPY_TESTLOGS_TO}" || exit_code=$?
fi

# TODO(yileiyang): Update and run smoke_test.sh.

exit $exit_code
