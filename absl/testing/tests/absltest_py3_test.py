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
"""Python3-only Tests for absltest."""

from absl.testing import absltest


class GetTestCaseNamesPEP3102Test(absltest.TestCase):
  """This test verifies absltest.TestLoader.GetTestCasesNames PEP3102 support.

    The test is Python3 only, as keyword only arguments are considered
    syntax error in Python2.

    The rest of getTestCaseNames functionality is covered
    by absltest_test.TestLoaderTest.
  """

  class Valid(absltest.TestCase):

    def testKeywordOnly(self, *, arg):
      pass

  def setUp(self):
    self.loader = absltest.TestLoader()
    super(GetTestCaseNamesPEP3102Test, self).setUp()

  def test_PEP3102_get_test_case_names(self):
    self.assertCountEqual(
        self.loader.getTestCaseNames(GetTestCaseNamesPEP3102Test.Valid),
        ["testKeywordOnly"])

if __name__ == "__main__":
  absltest.main()
