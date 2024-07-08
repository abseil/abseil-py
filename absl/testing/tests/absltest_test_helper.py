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

"""Helper binary for absltest_test.py."""

import os
import tempfile
import unittest

from absl import app
from absl import flags
from absl.testing import absltest

FLAGS = flags.FLAGS

_TEST_ID = flags.DEFINE_integer('test_id', 0, 'Which test to run.')
_NAME = flags.DEFINE_multi_string('name', [], 'List of names to print.')


@flags.validator('name')
def validate_name(value):
  # This validator makes sure that the second FLAGS(sys.argv) inside
  # absltest.main() won't actually trigger side effects of the flag parsing.
  if len(value) > 2:
    raise flags.ValidationError(
        f'No more than two names should be specified, found {len(value)} names')
  return True


class HelperTest(absltest.TestCase):

  def test_flags(self):
    if _TEST_ID.value == 1:
      self.assertEqual(FLAGS.test_random_seed, 301)
      if os.name == 'nt':
        # On Windows, it's always in the temp dir, which doesn't start with '/'.
        expected_prefix = tempfile.gettempdir()
      else:
        expected_prefix = '/'
      self.assertTrue(
          absltest.TEST_TMPDIR.value.startswith(expected_prefix),
          '--test_tmpdir={} does not start with {}'.format(
              absltest.TEST_TMPDIR.value, expected_prefix))
      self.assertTrue(os.access(absltest.TEST_TMPDIR.value, os.W_OK))
    elif _TEST_ID.value == 2:
      self.assertEqual(FLAGS.test_random_seed, 321)
      self.assertEqual(
          absltest.TEST_SRCDIR.value,
          os.environ['ABSLTEST_TEST_HELPER_EXPECTED_TEST_SRCDIR'])
      self.assertEqual(
          absltest.TEST_TMPDIR.value,
          os.environ['ABSLTEST_TEST_HELPER_EXPECTED_TEST_TMPDIR'])
    elif _TEST_ID.value == 3:
      self.assertEqual(FLAGS.test_random_seed, 123)
      self.assertEqual(
          absltest.TEST_SRCDIR.value,
          os.environ['ABSLTEST_TEST_HELPER_EXPECTED_TEST_SRCDIR'])
      self.assertEqual(
          absltest.TEST_TMPDIR.value,
          os.environ['ABSLTEST_TEST_HELPER_EXPECTED_TEST_TMPDIR'])
    elif _TEST_ID.value == 4:
      self.assertEqual(FLAGS.test_random_seed, 221)
      self.assertEqual(
          absltest.TEST_SRCDIR.value,
          os.environ['ABSLTEST_TEST_HELPER_EXPECTED_TEST_SRCDIR'])
      self.assertEqual(
          absltest.TEST_TMPDIR.value,
          os.environ['ABSLTEST_TEST_HELPER_EXPECTED_TEST_TMPDIR'])
    else:
      raise unittest.SkipTest(f'Not asked to run: --test_id={_TEST_ID.value}')

  @unittest.expectedFailure
  def test_expected_failure(self):
    if _TEST_ID.value == 5:
      self.assertEqual(1, 1)  # Expected failure, got success.
    else:
      self.assertEqual(1, 2)  # The expected failure.

  def test_xml_env_vars(self):
    if _TEST_ID.value == 6:
      self.assertEqual(
          FLAGS.xml_output_file,
          os.environ['ABSLTEST_TEST_HELPER_EXPECTED_XML_OUTPUT_FILE'])
    else:
      raise unittest.SkipTest(f'Not asked to run: --test_id={_TEST_ID.value}')

  def test_name_flag(self):
    if _TEST_ID.value == 7:
      print('Names in test_name_flag() are:', ' '.join(_NAME.value))
    else:
      raise unittest.SkipTest(f'Not asked to run: --test_id={_TEST_ID.value}')


class TempFileHelperTest(absltest.TestCase):
  """Helper test case for tempfile cleanup tests."""

  tempfile_cleanup = absltest.TempFileCleanup[os.environ.get(
      'ABSLTEST_TEST_HELPER_TEMPFILE_CLEANUP', 'SUCCESS')]

  def test_failure(self):
    self.create_tempfile('failure')
    self.fail('expected failure')

  def test_success(self):
    self.create_tempfile('success')

  def test_subtest_failure(self):
    self.create_tempfile('parent')
    with self.subTest('success'):
      self.create_tempfile('successful_child')
    with self.subTest('failure'):
      self.create_tempfile('failed_child')
      self.fail('expected failure')

  def test_subtest_success(self):
    self.create_tempfile('parent')
    for i in range(2):
      with self.subTest(f'success{i}'):
        self.create_tempfile(f'child{i}')


def main(argv):
  del argv  # Unused.
  print('Names in main() are:', ' '.join(_NAME.value))
  absltest.main()


if __name__ == '__main__':
  if os.environ.get('ABSLTEST_TEST_HELPER_USE_APP_RUN'):
    app.run(main)
  else:
    absltest.main()
