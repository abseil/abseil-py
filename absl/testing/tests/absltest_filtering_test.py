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

"""Tests for test filtering protocol."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import subprocess

from absl import logging
from absl.testing import _bazelize_command
from absl.testing import absltest


class TestFilteringTest(absltest.TestCase):
  """Integration tests: Runs a test binary with filtering.

  This is done by setting the filtering environment variable.
  """

  def setUp(self):
    self._test_path = os.path.join(
        os.path.dirname(__file__), 'absltest_filtering_test_helper')

  def _run_filtered(self, test_filter):
    """Runs the py_test binary in a subprocess.

    Args:
      test_filter: string, the filter argument to use.

    Returns:
      (stdout, exit_code) tuple of (string, int).
    """
    env = {}
    if 'SYSTEMROOT' in os.environ:
      # This is used by the random module on Windows to locate crypto
      # libraries.
      env['SYSTEMROOT'] = os.environ['SYSTEMROOT']
    if test_filter is not None:
      env['TESTBRIDGE_TEST_ONLY'] = test_filter

    proc = subprocess.Popen(
        args=[_bazelize_command.get_executable_path(self._test_path)],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True)
    stdout = proc.communicate()[0]

    logging.info('output: %s', stdout)
    return stdout, proc.wait()

  def test_no_filter(self):
    out, exit_code = self._run_filtered(None)
    self.assertEquals(1, exit_code)
    self.assertIn('class B test E', out)

  def test_empty_filter(self):
    out, exit_code = self._run_filtered('')
    self.assertEquals(1, exit_code)
    self.assertIn('class B test E', out)

  def test_class_filter(self):
    out, exit_code = self._run_filtered('ClassA')
    self.assertEquals(0, exit_code)
    self.assertNotIn('class B', out)

  def test_method_filter(self):
    out, exit_code = self._run_filtered('ClassB.testA')
    self.assertEquals(0, exit_code)
    self.assertNotIn('class A', out)
    self.assertNotIn('class B test B', out)

    out, exit_code = self._run_filtered('ClassB.testE')
    self.assertEquals(1, exit_code)
    self.assertNotIn('class A', out)

  def test_multiple_class_and_method_filter(self):
    out, exit_code = self._run_filtered(
        'ClassA.testA ClassA.testB ClassB.testC')
    self.assertEquals(0, exit_code)
    self.assertIn('class A test A', out)
    self.assertIn('class A test B', out)
    self.assertNotIn('class A test C', out)
    self.assertIn('class B test C', out)
    self.assertNotIn('class B test A', out)


if __name__ == '__main__':
  absltest.main()
