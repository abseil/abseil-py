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

"""Test of logging behavior before app.run(), aka flag and logging init()."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import io
import re

from absl import logging
from absl.testing import absltest
import mock

# We do this before our library imports in order to catch any Python stderr
# output they may generate.  We don't want them to; capture and check.
fake_stderr_type = io.BytesIO if bytes is str else io.StringIO

logging.get_verbosity()  # Access --verbosity before flag parsing.
# Access --logtostderr before flag parsing.
logging.get_absl_handler().use_absl_log_file()


class Error(Exception):
  pass


# Pre-initialization (aka "import" / __main__ time) test.  Checked below.
with mock.patch('sys.stderr', new=fake_stderr_type()) as pre_init_mock_stderr:
  # Trigger the notice to stderr once.  infos and above go to stderr.
  logging.debug('Debug message at parse time.')
  logging.info('Info message at parse time.')
  logging.error('Error message at parse time.')
  logging.warning('Warning message at parse time.')
  try:
    raise Error('Exception reason.')
  except Error:
    logging.exception('Exception message at parse time.')


class LoggingInitWarningTest(absltest.TestCase):

  def test_captured_pre_init_warnings(self):
    captured_stderr = pre_init_mock_stderr.getvalue()
    self.assertNotIn('Debug message at parse time.', captured_stderr)
    self.assertNotIn('Info message at parse time.', captured_stderr)

    traceback_re = re.compile(
        r'\nTraceback \(most recent call last\):.*?Error: Exception reason.',
        re.MULTILINE | re.DOTALL)
    if not traceback_re.search(captured_stderr):
      self.fail(
          'Cannot find traceback message from logging.exception '
          'in stderr:\n{}'.format(captured_stderr))
    # Remove the traceback so the rest of the stderr is deterministic.
    captured_stderr = traceback_re.sub('', captured_stderr)
    captured_stderr_lines = captured_stderr.splitlines()
    self.assertLen(captured_stderr_lines, 4)
    self.assertIn('Logging before flag parsing goes to stderr',
                  captured_stderr_lines[0])
    self.assertIn('Error message at parse time.', captured_stderr_lines[1])
    self.assertIn('Warning message at parse time.', captured_stderr_lines[2])
    self.assertIn('Exception message at parse time.', captured_stderr_lines[3])

  def test_no_more_warnings(self):
    with mock.patch('sys.stderr', new=fake_stderr_type()) as mock_stderr:
      self.assertMultiLineEqual('', mock_stderr.getvalue())
      logging.warning('Hello. hello. hello. Is there anybody out there?')
      self.assertNotIn('Logging before flag parsing goes to stderr',
                       mock_stderr.getvalue())
    logging.info('A major purpose of this executable is merely not to crash.')


if __name__ == '__main__':
  absltest.main()  # This calls the app.run() init equivalent.
