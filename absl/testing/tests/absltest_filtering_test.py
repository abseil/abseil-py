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

import subprocess
import sys

from absl import logging
from absl.testing import _bazelize_command
from absl.testing import absltest
from absl.testing import parameterized
from absl.testing.tests import absltest_env


@parameterized.named_parameters(
    ('as_env_variable_use_app_run', True, True),
    ('as_env_variable_no_argv', True, False),
    ('as_commandline_args_use_app_run', False, True),
    ('as_commandline_args_no_argv', False, False),
)
class TestFilteringTest(absltest.TestCase):
  """Integration tests: Runs a test binary with filtering.

  This is done by either setting the filtering environment variable, or passing
  the filters as command line arguments.
  """

  def setUp(self):
    super().setUp()
    self._test_name = 'absl/testing/tests/absltest_filtering_test_helper'

  def _run_filtered(self, test_filter, use_env_variable, use_app_run):
    """Runs the py_test binary in a subprocess.

    Args:
      test_filter: string, the filter argument to use.
      use_env_variable: bool, pass the test filter as environment variable if
        True, otherwise pass as command line arguments.
      use_app_run: bool, whether the test helper should call
        `absltest.main(argv=)` inside `app.run`.

    Returns:
      (stdout, exit_code) tuple of (string, int).
    """
    env = absltest_env.inherited_env()
    env['USE_APP_RUN'] = '1' if use_app_run else '0'
    additional_args = []
    if test_filter is not None:
      if use_env_variable:
        env['TESTBRIDGE_TEST_ONLY'] = test_filter
      elif test_filter:
        if sys.version_info[:2] >= (3, 7):
          # The -k flags are passed as positional arguments to absl.flags.
          additional_args.append('--')
          additional_args.extend(['-k=' + f for f in test_filter.split(' ')])
        else:
          additional_args.extend(test_filter.split(' '))

    proc = subprocess.Popen(
        args=([_bazelize_command.get_executable_path(self._test_name)] +
              additional_args),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True)
    stdout = proc.communicate()[0]

    logging.info('output: %s', stdout)
    return stdout, proc.wait()

  def test_no_filter(self, use_env_variable, use_app_run):
    out, exit_code = self._run_filtered(None, use_env_variable, use_app_run)
    self.assertEqual(1, exit_code)
    self.assertIn('class B test E', out)

  def test_empty_filter(self, use_env_variable, use_app_run):
    out, exit_code = self._run_filtered('', use_env_variable, use_app_run)
    self.assertEqual(1, exit_code)
    self.assertIn('class B test E', out)

  def test_class_filter(self, use_env_variable, use_app_run):
    out, exit_code = self._run_filtered('ClassA', use_env_variable, use_app_run)
    self.assertEqual(0, exit_code)
    self.assertNotIn('class B', out)

  def test_method_filter(self, use_env_variable, use_app_run):
    out, exit_code = self._run_filtered('ClassB.testA', use_env_variable,
                                        use_app_run)
    self.assertEqual(0, exit_code)
    self.assertNotIn('class A', out)
    self.assertNotIn('class B test B', out)

    out, exit_code = self._run_filtered('ClassB.testE', use_env_variable,
                                        use_app_run)
    self.assertEqual(1, exit_code)
    self.assertNotIn('class A', out)

  def test_multiple_class_and_method_filter(self, use_env_variable,
                                            use_app_run):
    out, exit_code = self._run_filtered(
        'ClassA.testA ClassA.testB ClassB.testC', use_env_variable, use_app_run)
    self.assertEqual(0, exit_code)
    self.assertIn('class A test A', out)
    self.assertIn('class A test B', out)
    self.assertNotIn('class A test C', out)
    self.assertIn('class B test C', out)
    self.assertNotIn('class B test A', out)

  @absltest.skipIf(
      sys.version_info[:2] < (3, 7),
      'Only Python 3.7+ does glob and substring matching.')
  def test_substring(self, use_env_variable, use_app_run):
    out, exit_code = self._run_filtered(
        'testA', use_env_variable, use_app_run)
    self.assertEqual(0, exit_code)
    self.assertIn('Ran 2 tests', out)
    self.assertIn('ClassA.testA', out)
    self.assertIn('ClassB.testA', out)

  @absltest.skipIf(
      sys.version_info[:2] < (3, 7),
      'Only Python 3.7+ does glob and substring matching.')
  def test_glob_pattern(self, use_env_variable, use_app_run):
    out, exit_code = self._run_filtered(
        '__main__.Class*.testA', use_env_variable, use_app_run)
    self.assertEqual(0, exit_code)
    self.assertIn('Ran 2 tests', out)
    self.assertIn('ClassA.testA', out)
    self.assertIn('ClassB.testA', out)

  @absltest.skipIf(
      sys.version_info[:2] >= (3, 7),
      "Python 3.7+ uses unittest's -k flag and doesn't fail if no tests match.")
  def test_not_found_filters_py36(self, use_env_variable, use_app_run):
    out, exit_code = self._run_filtered('NotExistedClass.not_existed_method',
                                        use_env_variable, use_app_run)
    self.assertEqual(1, exit_code)
    self.assertIn("has no attribute 'NotExistedClass'", out)

  @absltest.skipIf(
      sys.version_info[:2] < (3, 7),
      'Python 3.6 passes the filter as positional arguments and fails if no '
      'tests match.'
  )
  def test_not_found_filters_py37(self, use_env_variable, use_app_run):
    out, exit_code = self._run_filtered('NotExistedClass.not_existed_method',
                                        use_env_variable, use_app_run)
    self.assertEqual(0, exit_code)
    self.assertIn('Ran 0 tests', out)

  @absltest.skipIf(
      sys.version_info[:2] < (3, 7),
      'Python 3.6 passes the filter as positional arguments and matches by name'
  )
  def test_parameterized_unnamed(self, use_env_variable, use_app_run):
    out, exit_code = self._run_filtered('ParameterizedTest.test_unnamed',
                                        use_env_variable, use_app_run)
    self.assertEqual(0, exit_code)
    self.assertIn('Ran 2 tests', out)
    self.assertIn('parameterized unnamed 1', out)
    self.assertIn('parameterized unnamed 2', out)

  @absltest.skipIf(
      sys.version_info[:2] < (3, 7),
      'Python 3.6 passes the filter as positional arguments and matches by name'
  )
  def test_parameterized_named(self, use_env_variable, use_app_run):
    out, exit_code = self._run_filtered('ParameterizedTest.test_named',
                                        use_env_variable, use_app_run)
    self.assertEqual(0, exit_code)
    self.assertIn('Ran 2 tests', out)
    self.assertIn('parameterized named 1', out)
    self.assertIn('parameterized named 2', out)


if __name__ == '__main__':
  absltest.main()
