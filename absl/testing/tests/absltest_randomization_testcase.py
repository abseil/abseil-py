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

"""Stub tests, only for use in absltest_randomization_test.py."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys

from absl.testing import absltest


# This stanza exercises setting $TEST_RANDOMIZE_ORDERING_SEED *after* importing
# the absltest library.
if os.environ.get('LATE_SET_TEST_RANDOMIZE_ORDERING_SEED', ''):
  os.environ['TEST_RANDOMIZE_ORDERING_SEED'] = os.environ[
      'LATE_SET_TEST_RANDOMIZE_ORDERING_SEED']


class ClassA(absltest.TestCase):

  def test_a(self):
    sys.stderr.write('\nclass A test A\n')

  def test_b(self):
    sys.stderr.write('\nclass A test B\n')

  def test_c(self):
    sys.stderr.write('\nclass A test C\n')


if __name__ == '__main__':
  absltest.main()
