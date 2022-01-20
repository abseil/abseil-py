"""Helper library to get environment variables for absltest helper binaries."""

import os


_INHERITED_ENV_KEYS = frozenset({
    # This is needed to correctly use the Python interpreter determined by
    # bazel.
    'PATH',
    # This is used by the random module on Windows to locate crypto
    # libraries.
    'SYSTEMROOT',
})


def inherited_env():
  """Returns the environment variables that should be inherited from parent.

  Reason why using an explicit list of environment variables instead of
  inheriting all from parent: the absltest module itself interprets a list of
  environment variables set by bazel, e.g. XML_OUTPUT_FILE,
  TESTBRIDGE_TEST_ONLY. While testing absltest's own behavior, we should
  remove them when invoking the helper subprocess. Using an explicit list is
  safer.
  """
  env = {}
  for key in _INHERITED_ENV_KEYS:
    if key in os.environ:
      env[key] = os.environ[key]
  return env
