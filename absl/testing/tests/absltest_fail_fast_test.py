# Copyright 2020 The Abseil Authors.
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

"""Tests for test fail fast protocol."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import subprocess

from absl import logging
from absl.testing import _bazelize_command
from absl.testing import absltest
from absl.testing import parameterized
from absl.testing.tests import absltest_env


@parameterized.named_parameters(
    ('use_app_run', True),
    ('no_argv', False),
)
class TestFailFastTest(parameterized.TestCase):
  """Integration tests: Runs a test binary with fail fast.

  This is done by setting the fail fast environment variable
  """

  def setUp(self):
    super().setUp()
    self._test_name = 'absl/testing/tests/absltest_fail_fast_test_helper'

  def _run_fail_fast(self, fail_fast, use_app_run):
    """Runs the py_test binary in a subprocess.

    Args:
      fail_fast: string, the fail fast value.
      use_app_run: bool, whether the test helper should call
          `absltest.main(argv=)` inside `app.run`.

    Returns:
      (stdout, exit_code) tuple of (string, int).
    """
    env = absltest_env.inherited_env()
    if fail_fast is not None:
      env['TESTBRIDGE_TEST_RUNNER_FAIL_FAST'] = fail_fast
    env['USE_APP_RUN'] = '1' if use_app_run else '0'

    proc = subprocess.Popen(
        args=[_bazelize_command.get_executable_path(self._test_name)],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True)
    stdout = proc.communicate()[0]

    logging.info('output: %s', stdout)
    return stdout, proc.wait()

  def test_no_fail_fast(self, use_app_run):
    out, exit_code = self._run_fail_fast(None, use_app_run)
    self.assertEqual(1, exit_code)
    self.assertIn('class A test A', out)
    self.assertIn('class A test B', out)
    self.assertIn('class A test C', out)
    self.assertIn('class A test D', out)
    self.assertIn('class A test E', out)

  def test_empty_fail_fast(self, use_app_run):
    out, exit_code = self._run_fail_fast('', use_app_run)
    self.assertEqual(1, exit_code)
    self.assertIn('class A test A', out)
    self.assertIn('class A test B', out)
    self.assertIn('class A test C', out)
    self.assertIn('class A test D', out)
    self.assertIn('class A test E', out)

  def test_fail_fast_1(self, use_app_run):
    out, exit_code = self._run_fail_fast('1', use_app_run)
    self.assertEqual(1, exit_code)
    self.assertIn('class A test A', out)
    self.assertIn('class A test B', out)
    self.assertIn('class A test C', out)
    self.assertNotIn('class A test D', out)
    self.assertNotIn('class A test E', out)

  def test_fail_fast_0(self, use_app_run):
    out, exit_code = self._run_fail_fast('0', use_app_run)
    self.assertEqual(1, exit_code)
    self.assertIn('class A test A', out)
    self.assertIn('class A test B', out)
    self.assertIn('class A test C', out)
    self.assertIn('class A test D', out)
    self.assertIn('class A test E', out)


if __name__ == '__main__':
  absltest.main()
