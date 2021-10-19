# Copyright 2021 The Abseil Authors.
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
"""Test that verifies the Python version used in bazel is expected."""

import sys
from absl import flags
from absl.testing import absltest

_EXPECTED_VERSION = flags.DEFINE_string(
    'expected_version',
    None,
    'The expected Python SemVer version, '
    'can be major.minor or major.minor.patch.',
)


class PythonVersionTest(absltest.TestCase):

  def test_version(self):
    version = _EXPECTED_VERSION.value
    if not version:
      self.skipTest(
          'Skipping version test since --expected_version is not specified')
    num_parts = len(version.split('.'))
    self.assertEqual('.'.join(map(str, sys.version_info[:num_parts])), version)


if __name__ == '__main__':
  absltest.main()
