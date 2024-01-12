"""Test helper for ExitCodeTest in absltest_test.py."""

import os
from absl.testing import absltest


if os.environ.get("ABSLTEST_TEST_HELPER_DEFINE_CLASS") == "1":

  class MyTest(absltest.TestCase):

    @absltest.skip("Skipped for testing the exit code behavior")
    def test_foo(self):
      pass


if __name__ == "__main__":
  absltest.main()
