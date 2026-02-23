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

import logging

from absl import logging as absl_logging
from absl.logging import converter
from absl.testing import absltest
from absl.testing import parameterized


class ConverterTest(parameterized.TestCase):
  """Tests the converter module."""

  @parameterized.parameters([
      (absl_logging.DEBUG, 0),
      (absl_logging.INFO, 0),
      (absl_logging.WARN, 1),
      (absl_logging.ERROR, 2),
      (absl_logging.FATAL, 3),
      (100, 0),
  ])
  def test_absl_to_cpp(self, absl_level: int, expected_cpp_level: int):
    self.assertEqual(expected_cpp_level, converter.absl_to_cpp(absl_level))

  def test_absl_to_cpp_raises_on_invalid_input(self):
    with self.assertRaises(TypeError):
      converter.absl_to_cpp('')

  @parameterized.parameters([
      (absl_logging.DEBUG, logging.DEBUG),
      (absl_logging.INFO, logging.INFO),
      (absl_logging.WARN, logging.WARNING),
      (absl_logging.WARN, logging.WARN),
      (absl_logging.ERROR, logging.ERROR),
      (absl_logging.FATAL, logging.FATAL),
      (absl_logging.FATAL, logging.CRITICAL),
      # vlog levels:
      (2, 9),
      (3, 8),
  ])
  def test_absl_to_standard(
      self, absl_level: int, expected_standard_level: int
  ):
    self.assertEqual(
        expected_standard_level, converter.absl_to_standard(absl_level)
    )

  def test_absl_to_standard_raises_on_invalid_input(self):
    with self.assertRaises(TypeError):
      converter.absl_to_standard('')

  @parameterized.parameters([
      (logging.DEBUG, absl_logging.DEBUG),
      (logging.INFO, absl_logging.INFO),
      (logging.WARN, absl_logging.WARN),
      (logging.WARNING, absl_logging.WARN),
      (logging.ERROR, absl_logging.ERROR),
      (logging.FATAL, absl_logging.FATAL),
      (logging.CRITICAL, absl_logging.FATAL),
      # vlog levels:
      (logging.DEBUG - 1, 2),
      (logging.DEBUG - 2, 3),
  ])
  def test_standard_to_absl(
      self, standard_level: int, expected_absl_level: int
  ):
    self.assertEqual(
        expected_absl_level, converter.standard_to_absl(standard_level)
    )

  def test_standard_to_absl_raises_on_invalid_input(self):
    with self.assertRaises(TypeError):
      converter.standard_to_absl('')

  @parameterized.parameters([
      (logging.DEBUG, 0),
      (logging.INFO, 0),
      (logging.WARN, 1),
      (logging.WARNING, 1),
      (logging.ERROR, 2),
      (logging.FATAL, 3),
      (logging.CRITICAL, 3),
  ])
  def test_standard_to_cpp(self, standard_level: int, expected_cpp_level: int):
    self.assertEqual(
        expected_cpp_level, converter.standard_to_cpp(standard_level)
    )

  def test_standard_to_cpp_raises_on_invalid_input(self):
    with self.assertRaises(TypeError):
      converter.standard_to_cpp('')

  @parameterized.parameters([
      (logging.CRITICAL, 'F'),
      (logging.ERROR, 'E'),
      (logging.WARNING, 'W'),
      (logging.INFO, 'I'),
      (logging.DEBUG, 'I'),
      (logging.NOTSET, 'I'),
      (51, 'F'),
      (49, 'E'),
      (41, 'E'),
      (39, 'W'),
      (31, 'W'),
      (29, 'I'),
      (21, 'I'),
      (19, 'I'),
      (11, 'I'),
      (9, 'I'),
      (1, 'I'),
      (-1, 'I'),
  ])
  def test_get_initial_for_level(self, level: int, expected_initial: str):
    self.assertEqual(expected_initial, converter.get_initial_for_level(level))

  @parameterized.parameters([
      ('debug', logging.DEBUG),
      ('info', logging.INFO),
      ('warn', logging.WARNING),
      ('warning', logging.WARNING),
      ('error', logging.ERROR),
      ('fatal', logging.CRITICAL),
      ('DEBUG', logging.DEBUG),
      ('INFO', logging.INFO),
      ('WARN', logging.WARNING),
      ('WARNING', logging.WARNING),
      ('ERROR', logging.ERROR),
      ('FATAL', logging.CRITICAL),
  ])
  def test_string_to_standard(self, level_string: str, expected_level: int):
    self.assertEqual(expected_level, converter.string_to_standard(level_string))


if __name__ == '__main__':
  absltest.main()
