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

"""Additional tests for flag argument parsers.

Most of the argument parsers are covered in the flags_test.py.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl.flags import _argument_parser
from absl.testing import absltest


class ArgumentParserTest(absltest.TestCase):

  def test_instance_cache(self):
    parser1 = _argument_parser.FloatParser()
    parser2 = _argument_parser.FloatParser()
    self.assertIs(parser1, parser2)

  def test_parse_wrong_type(self):
    parser = _argument_parser.ArgumentParser()
    with self.assertRaises(TypeError):
      parser.parse(0)

    if bytes is not str:
      # In PY3, it does not accept bytes.
      with self.assertRaises(TypeError):
        parser.parse(b'')


class FloatParserTest(absltest.TestCase):

  def setUp(self):
    self.parser = _argument_parser.FloatParser()

  def test_parse_string(self):
    self.assertEqual(1.5, self.parser.parse('1.5'))

  def test_parse_wrong_type(self):
    with self.assertRaises(TypeError):
      self.parser.parse(False)


class IntegerParserTest(absltest.TestCase):

  def setUp(self):
    self.parser = _argument_parser.IntegerParser()

  def test_parse_string(self):
    self.assertEqual(1, self.parser.parse('1'))

  def test_parse_wrong_type(self):
    with self.assertRaises(TypeError):
      self.parser.parse(1e2)
    with self.assertRaises(TypeError):
      self.parser.parse(False)


class EnumParserTest(absltest.TestCase):

  def test_empty_values(self):
    with self.assertRaises(ValueError):
      _argument_parser.EnumParser([])

  def test_parse(self):
    parser = _argument_parser.EnumParser(['apple', 'banana'])
    self.assertEqual('apple', parser.parse('apple'))

  def test_parse_not_found(self):
    parser = _argument_parser.EnumParser(['apple', 'banana'])
    with self.assertRaises(ValueError):
      parser.parse('orange')


class HelperFunctionsTest(absltest.TestCase):

  def test_is_integer_type(self):
    self.assertTrue(_argument_parser._is_integer_type(1))
    # Note that isinstance(False, int) == True.
    self.assertFalse(_argument_parser._is_integer_type(False))


if __name__ == '__main__':
  absltest.main()
