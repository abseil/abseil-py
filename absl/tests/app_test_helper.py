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

"""Helper script used by app_unittest.sh."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys

try:
  import faulthandler
except ImportError:
  faulthandler = None

from absl import app
from absl import flags

FLAGS = flags.FLAGS
flags.DEFINE_boolean('faulthandler_sigsegv', False, 'raise SIGSEGV')
flags.DEFINE_boolean('raise_exception', False, 'Raise MyException from main.')
flags.DEFINE_boolean(
    'raise_usage_error', False, 'Raise app.UsageError from main.')
flags.DEFINE_integer(
    'usage_error_exitcode', None, 'The exitcode if app.UsageError if raised.')


called_main_function_name = None


class MyException(Exception):
  pass


class MyExceptionHandler(app.ExceptionHandler):

  def __init__(self, message):
    self.message = message

  def handle(self, exc):
    sys.stdout.write('MyExceptionHandler: {}\n'.format(self.message))


def real_main(argv):
  """The main function."""
  if os.environ.get('APP_TEST_PRINT_ARGV', False):
    sys.stdout.write('argv: {}\n'.format(' '.join(argv)))

  if FLAGS.raise_exception:
    raise MyException

  if FLAGS.raise_usage_error:
    if FLAGS.usage_error_exitcode is not None:
      raise app.UsageError('Error!', FLAGS.usage_error_exitcode)
    else:
      raise app.UsageError('Error!')

  if FLAGS.faulthandler_sigsegv:
    faulthandler._sigsegv()  # pylint: disable=protected-access
    sys.exit(1)  # Should not reach here.

  # Ensure that we have a random C++ flag in flags.FLAGS; this shows
  # us that app.run() did the right thing in conjunction with C++ flags.
  helper_type = os.environ['APP_TEST_HELPER_TYPE']
  if helper_type == 'clif':
    if 'heap_check_before_constructors' in flags.FLAGS:
      print('PASS: C++ flag present and helper_type is {}'.format(helper_type))
      sys.exit(0)
    else:
      print('FAILED: C++ flag absent but helper_type is {}'.format(helper_type))
      sys.exit(1)
  elif helper_type == 'pure_python':
    if 'heap_check_before_constructors' in flags.FLAGS:
      print('FAILED: C++ flag present but helper_type is pure_python')
      sys.exit(1)
    else:
      print('PASS: C++ flag absent and helper_type is pure_python')
      sys.exit(0)
  else:
    print('Unexpected helper_type "{}"'.format(helper_type))
    sys.exit(1)
  # MOE:end_strip


def custom_main(argv):
  global called_main_function_name
  called_main_function_name = 'custom_main'

  real_main(argv)


def main(argv):
  global called_main_function_name
  called_main_function_name = 'main'

  real_main(argv)


if __name__ == '__main__':
  use_custom_main = os.environ.get('APP_TEST_USE_CUSTOM_MAIN', False)
  if use_custom_main:
    main_func = custom_main
  else:
    main_func = main
  custom_argv = os.environ.get('APP_TEST_CUSTOM_ARGV', None)
  if custom_argv:
    custom_argv = custom_argv.split(' ')
  else:
    custom_argv = None

  app.install_exception_handler(MyExceptionHandler('first'))
  app.install_exception_handler(MyExceptionHandler('second'))
  app.run(main=main_func, argv=custom_argv)

  if main_func:
    if called_main_function_name != 'custom_main':
      print('called_main_function_name should be custom_main, found %s.',
            called_main_function_name)
      sys.exit(1)
