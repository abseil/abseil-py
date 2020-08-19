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

import os
import subprocess

from absl import logging
from absl.testing import _bazelize_command
from absl.testing import absltest


class TestFailFastTest(absltest.TestCase):
  """Integration tests: Runs a test binary with fail fast.

  This is done by setting the fail fast environment variable
  """

  def setUp(self):
    self._test_name = 'absl/testing/tests/absltest_fail_fast_test_helper'

  def _run_fail_fast(self, fail_fast):
    """Runs the py_test binary in a subprocess.

    Args:
      fail_fast: string, the fail fast value.

    Returns:
      (stdout, exit_code) tuple of (string, int).
    """
    env = {}
    if 'SYSTEMROOT' in os.environ:
      # This is used by the random module on Windows to locate crypto
      # libraries.
      env['SYSTEMROOT'] = os.environ['SYSTEMROOT']
    additional_args = []
    if fail_fast is not None:
      env['TESTBRIDGE_TEST_RUNNER_FAIL_FAST'] = fail_fast

    proc = subprocess.Popen(
        args=([_bazelize_command.get_executable_path(self._test_name)]
              + additional_args),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True)
    stdout = proc.communicate()[0]

    logging.info('output: %s', stdout)
    return stdout, proc.wait()

  def test_no_fail_fast(self):
    out, exit_code = self._run_fail_fast(None)
    self.assertEqual(1, exit_code)
    self.assertIn('class A test A', out)
    self.assertIn('class A test B', out)
    self.assertIn('class A test C', out)
    self.assertIn('class A test D', out)
    self.assertIn('class A test E', out)

  def test_empty_fail_fast(self):
    out, exit_code = self._run_fail_fast('')
    self.assertEqual(1, exit_code)
    self.assertIn('class A test A', out)
    self.assertIn('class A test B', out)
    self.assertIn('class A test C', out)
    self.assertIn('class A test D', out)
    self.assertIn('class A test E', out)

  def test_fail_fast_1(self):
    out, exit_code = self._run_fail_fast('1')
    self.assertEqual(1, exit_code)
    self.assertIn('class A test A', out)
    self.assertIn('class A test B', out)
    self.assertIn('class A test C', out)
    self.assertNotIn('class A test D', out)
    self.assertNotIn('class A test E', out)

  def test_fail_fast_0(self):
    out, exit_code = self._run_fail_fast('0')
    self.assertEqual(1, exit_code)
    self.assertIn('class A test A', out)
    self.assertIn('class A test B', out)
    self.assertIn('class A test C', out)
    self.assertIn('class A test D', out)
    self.assertIn('class A test E', out)


if __name__ == '__main__':
  absltest.main()
