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

import enum

from absl.flags import _argument_parser
from absl.testing import absltest
from absl.testing import parameterized


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


class BooleanParserTest(absltest.TestCase):

  def setUp(self):
    super().setUp()
    self.parser = _argument_parser.BooleanParser()

  def test_parse_bytes(self):
    with self.assertRaises(TypeError):
      self.parser.parse(b'true')

  def test_parse_str(self):
    self.assertTrue(self.parser.parse('true'))

  def test_parse_unicode(self):
    self.assertTrue(self.parser.parse(u'true'))

  def test_parse_wrong_type(self):
    with self.assertRaises(TypeError):
      self.parser.parse(1.234)

  def test_parse_str_false(self):
    self.assertFalse(self.parser.parse('false'))

  def test_parse_integer(self):
    self.assertTrue(self.parser.parse(1))

  def test_parse_invalid_integer(self):
    with self.assertRaises(ValueError):
      self.parser.parse(-1)

  def test_parse_invalid_str(self):
    with self.assertRaises(ValueError):
      self.parser.parse('nottrue')


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


class Fruit(enum.Enum):
  APPLE = 1
  BANANA = 2


class EmptyEnum(enum.Enum):
  pass


class MixedCaseEnum(enum.Enum):
  APPLE = 1
  BANANA = 2
  apple = 3


class EnumClassParserTest(parameterized.TestCase):

  def test_requires_enum(self):
    with self.assertRaises(TypeError):
      _argument_parser.EnumClassParser(['apple', 'banana'])

  def test_requires_non_empty_enum_class(self):
    with self.assertRaises(ValueError):
      _argument_parser.EnumClassParser(EmptyEnum)

  def test_case_sensitive_rejects_duplicates(self):
    unused_normal_parser = _argument_parser.EnumClassParser(MixedCaseEnum)
    with self.assertRaisesRegex(ValueError, 'Duplicate.+apple'):
      _argument_parser.EnumClassParser(MixedCaseEnum, case_sensitive=False)

  def test_parse_string(self):
    parser = _argument_parser.EnumClassParser(Fruit)
    self.assertEqual(Fruit.APPLE, parser.parse('APPLE'))

  def test_parse_string_case_sensitive(self):
    parser = _argument_parser.EnumClassParser(Fruit)
    with self.assertRaises(ValueError):
      parser.parse('apple')

  @parameterized.parameters('APPLE', 'apple', 'Apple')
  def test_parse_string_case_insensitive(self, value):
    parser = _argument_parser.EnumClassParser(Fruit, case_sensitive=False)
    self.assertIs(Fruit.APPLE, parser.parse(value))

  def test_parse_literal(self):
    parser = _argument_parser.EnumClassParser(Fruit)
    self.assertEqual(Fruit.APPLE, parser.parse(Fruit.APPLE))

  def test_parse_not_found(self):
    parser = _argument_parser.EnumClassParser(Fruit)
    with self.assertRaises(ValueError):
      parser.parse('ORANGE')

  @parameterized.parameters((Fruit.BANANA, False, 'BANANA'),
                            (Fruit.BANANA, True, 'banana'))
  def test_serialize_parse(self, value, lowercase, expected):
    serializer = _argument_parser.EnumClassSerializer(lowercase=lowercase)
    parser = _argument_parser.EnumClassParser(
        Fruit, case_sensitive=not lowercase)
    serialized = serializer.serialize(value)
    self.assertEqual(serialized, expected)
    self.assertEqual(value, parser.parse(expected))


class SerializerTest(parameterized.TestCase):

  def test_csv_serializer(self):
    serializer = _argument_parser.CsvListSerializer('+')
    self.assertEqual(serializer.serialize(['foo', 'bar']), 'foo+bar')

  @parameterized.parameters([
      dict(lowercase=False, expected='APPLE+BANANA'),
      dict(lowercase=True, expected='apple+banana'),
  ])
  def test_enum_class_list_serializer(self, lowercase, expected):
    values = [Fruit.APPLE, Fruit.BANANA]
    serializer = _argument_parser.EnumClassListSerializer(
        list_sep='+', lowercase=lowercase)
    serialized = serializer.serialize(values)
    self.assertEqual(expected, serialized)


class HelperFunctionsTest(absltest.TestCase):

  def test_is_integer_type(self):
    self.assertTrue(_argument_parser._is_integer_type(1))
    # Note that isinstance(False, int) == True.
    self.assertFalse(_argument_parser._is_integer_type(False))


if __name__ == '__main__':
  absltest.main()
