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

"""Tests for absltest."""

import collections
from collections.abc import Mapping
import contextlib
import dataclasses
import os
import pathlib
import re
import stat
import string
import subprocess
import sys
import tempfile
import textwrap
from typing import Any, ItemsView, Iterator, KeysView, Mapping, Optional, Type, ValuesView
import unittest

from absl.testing import _bazelize_command
from absl.testing import absltest
from absl.testing import parameterized
from absl.testing.tests import absltest_env


class TestMapping(Mapping):

  def __init__(self, *args, **kwargs):
    self._dict = dict(*args, **kwargs)

  def __getitem__(self, key):
    return self._dict[key]

  def __len__(self):
    return len(self._dict)

  def __iter__(self):
    return iter(self._dict)


class BaseTestCase(parameterized.TestCase):

  def _get_helper_exec_path(self, helper_name):
    helper = 'absl/testing/tests/' + helper_name
    return _bazelize_command.get_executable_path(helper)

  def run_helper(
      self,
      test_id,
      args,
      env_overrides,
      expect_success,
      helper_name=None,
  ):
    env = absltest_env.inherited_env()
    for key, value in env_overrides.items():
      if value is None:
        if key in env:
          del env[key]
      else:
        env[key] = value

    if helper_name is None:
      helper_name = 'absltest_test_helper'
    command = [self._get_helper_exec_path(helper_name)]
    if test_id is not None:
      command.append(f'--test_id={test_id}')
    command.extend(args)
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
        universal_newlines=True)
    stdout, stderr = process.communicate()
    if expect_success:
      self.assertEqual(
          0,
          process.returncode,
          'Expected success, but failed with exit code {},'
          ' stdout:\n{}\nstderr:\n{}\n'.format(
              process.returncode, stdout, stderr
          ),
      )
    else:
      self.assertGreater(
          process.returncode,
          0,
          'Expected failure, but succeeded with '
          'stdout:\n{}\nstderr:\n{}\n'.format(stdout, stderr),
      )
    return stdout, stderr, process.returncode


class TestCaseTest(BaseTestCase):
  longMessage = True

  def run_helper(
      self, test_id, args, env_overrides, expect_success, helper_name=None
  ):
    return super().run_helper(
        test_id,
        args + ['HelperTest'],
        env_overrides,
        expect_success,
        helper_name,
    )

  def test_flags_no_env_var_no_flags(self):
    self.run_helper(
        1,
        [],
        {'TEST_RANDOM_SEED': None,
         'TEST_SRCDIR': None,
         'TEST_TMPDIR': None,
        },
        expect_success=True)

  def test_flags_env_var_no_flags(self):
    tmpdir = tempfile.mkdtemp(dir=absltest.TEST_TMPDIR.value)
    srcdir = tempfile.mkdtemp(dir=absltest.TEST_TMPDIR.value)
    self.run_helper(
        2,
        [],
        {'TEST_RANDOM_SEED': '321',
         'TEST_SRCDIR': srcdir,
         'TEST_TMPDIR': tmpdir,
         'ABSLTEST_TEST_HELPER_EXPECTED_TEST_SRCDIR': srcdir,
         'ABSLTEST_TEST_HELPER_EXPECTED_TEST_TMPDIR': tmpdir,
        },
        expect_success=True)

  def test_flags_no_env_var_flags(self):
    tmpdir = tempfile.mkdtemp(dir=absltest.TEST_TMPDIR.value)
    srcdir = tempfile.mkdtemp(dir=absltest.TEST_TMPDIR.value)
    self.run_helper(
        3,
        [
            '--test_random_seed=123',
            f'--test_srcdir={srcdir}',
            f'--test_tmpdir={tmpdir}',
        ],
        {
            'TEST_RANDOM_SEED': None,
            'TEST_SRCDIR': None,
            'TEST_TMPDIR': None,
            'ABSLTEST_TEST_HELPER_EXPECTED_TEST_SRCDIR': srcdir,
            'ABSLTEST_TEST_HELPER_EXPECTED_TEST_TMPDIR': tmpdir,
        },
        expect_success=True,
    )

  def test_flags_env_var_flags(self):
    tmpdir_from_flag = tempfile.mkdtemp(dir=absltest.TEST_TMPDIR.value)
    srcdir_from_flag = tempfile.mkdtemp(dir=absltest.TEST_TMPDIR.value)
    tmpdir_from_env_var = tempfile.mkdtemp(dir=absltest.TEST_TMPDIR.value)
    srcdir_from_env_var = tempfile.mkdtemp(dir=absltest.TEST_TMPDIR.value)
    self.run_helper(
        4,
        [
            '--test_random_seed=221',
            f'--test_srcdir={srcdir_from_flag}',
            f'--test_tmpdir={tmpdir_from_flag}',
        ],
        {
            'TEST_RANDOM_SEED': '123',
            'TEST_SRCDIR': srcdir_from_env_var,
            'TEST_TMPDIR': tmpdir_from_env_var,
            'ABSLTEST_TEST_HELPER_EXPECTED_TEST_SRCDIR': srcdir_from_flag,
            'ABSLTEST_TEST_HELPER_EXPECTED_TEST_TMPDIR': tmpdir_from_flag,
        },
        expect_success=True,
    )

  def test_xml_output_file_from_xml_output_file_env(self):
    xml_dir = tempfile.mkdtemp(dir=absltest.TEST_TMPDIR.value)
    xml_output_file_env = os.path.join(xml_dir, 'xml_output_file.xml')
    random_dir = tempfile.mkdtemp(dir=absltest.TEST_TMPDIR.value)
    self.run_helper(
        6,
        [],
        {'XML_OUTPUT_FILE': xml_output_file_env,
         'RUNNING_UNDER_TEST_DAEMON': '1',
         'TEST_XMLOUTPUTDIR': random_dir,
         'ABSLTEST_TEST_HELPER_EXPECTED_XML_OUTPUT_FILE': xml_output_file_env,
        },
        expect_success=True)

  def test_xml_output_file_from_daemon(self):
    tmpdir = os.path.join(tempfile.mkdtemp(
        dir=absltest.TEST_TMPDIR.value), 'sub_dir')
    random_dir = tempfile.mkdtemp(dir=absltest.TEST_TMPDIR.value)
    self.run_helper(
        6,
        ['--test_tmpdir', tmpdir],
        {'XML_OUTPUT_FILE': None,
         'RUNNING_UNDER_TEST_DAEMON': '1',
         'TEST_XMLOUTPUTDIR': random_dir,
         'ABSLTEST_TEST_HELPER_EXPECTED_XML_OUTPUT_FILE': os.path.join(
             os.path.dirname(tmpdir), 'test_detail.xml'),
        },
        expect_success=True)

  def test_xml_output_file_from_test_xmloutputdir_env(self):
    xml_output_dir = tempfile.mkdtemp(dir=absltest.TEST_TMPDIR.value)
    expected_xml_file = 'absltest_test_helper.xml'
    self.run_helper(
        6,
        [],
        {'XML_OUTPUT_FILE': None,
         'RUNNING_UNDER_TEST_DAEMON': None,
         'TEST_XMLOUTPUTDIR': xml_output_dir,
         'ABSLTEST_TEST_HELPER_EXPECTED_XML_OUTPUT_FILE': os.path.join(
             xml_output_dir, expected_xml_file),
        },
        expect_success=True)

  def test_xml_output_file_from_flag(self):
    random_dir = tempfile.mkdtemp(dir=absltest.TEST_TMPDIR.value)
    flag_file = os.path.join(
        tempfile.mkdtemp(dir=absltest.TEST_TMPDIR.value), 'output.xml')
    self.run_helper(
        6,
        ['--xml_output_file', flag_file],
        {'XML_OUTPUT_FILE': os.path.join(random_dir, 'output.xml'),
         'RUNNING_UNDER_TEST_DAEMON': '1',
         'TEST_XMLOUTPUTDIR': random_dir,
         'ABSLTEST_TEST_HELPER_EXPECTED_XML_OUTPUT_FILE': flag_file,
        },
        expect_success=True)

  def test_app_run(self):
    stdout, _, _ = self.run_helper(
        7,
        ['--name=cat', '--name=dog'],
        {'ABSLTEST_TEST_HELPER_USE_APP_RUN': '1'},
        expect_success=True,
    )
    self.assertIn('Names in main() are: cat dog', stdout)
    self.assertIn('Names in test_name_flag() are: cat dog', stdout)

  def test_assert_in(self):
    animals = {'monkey': 'banana', 'cow': 'grass', 'seal': 'fish'}

    self.assertIn('a', 'abc')
    self.assertIn(2, [1, 2, 3])
    self.assertIn('monkey', animals)

    self.assertNotIn('d', 'abc')
    self.assertNotIn(0, [1, 2, 3])
    self.assertNotIn('otter', animals)

    self.assertRaises(AssertionError, self.assertIn, 'x', 'abc')
    self.assertRaises(AssertionError, self.assertIn, 4, [1, 2, 3])
    self.assertRaises(AssertionError, self.assertIn, 'elephant', animals)

    self.assertRaises(AssertionError, self.assertNotIn, 'c', 'abc')
    self.assertRaises(AssertionError, self.assertNotIn, 1, [1, 2, 3])
    self.assertRaises(AssertionError, self.assertNotIn, 'cow', animals)

  @absltest.expectedFailure
  def test_expected_failure(self):
    self.assertEqual(1, 2)  # the expected failure

  @absltest.expectedFailureIf(True, 'always true')
  def test_expected_failure_if(self):
    self.assertEqual(1, 2)  # the expected failure

  def test_expected_failure_success(self):
    _, stderr, _ = self.run_helper(5, ['--', '-v'], {}, expect_success=False)
    self.assertRegex(stderr, r'FAILED \(.*unexpected successes=1\)')

  def test_assert_equal(self):
    self.assertListEqual([], [])
    self.assertTupleEqual((), ())
    self.assertSequenceEqual([], ())

    a = [0, 'a', []]
    b = []
    self.assertRaises(absltest.TestCase.failureException,
                      self.assertListEqual, a, b)
    self.assertRaises(absltest.TestCase.failureException,
                      self.assertListEqual, tuple(a), tuple(b))
    self.assertRaises(absltest.TestCase.failureException,
                      self.assertSequenceEqual, a, tuple(b))

    b.extend(a)
    self.assertListEqual(a, b)
    self.assertTupleEqual(tuple(a), tuple(b))
    self.assertSequenceEqual(a, tuple(b))
    self.assertSequenceEqual(tuple(a), b)

    self.assertRaises(AssertionError, self.assertListEqual, a, tuple(b))
    self.assertRaises(AssertionError, self.assertTupleEqual, tuple(a), b)
    self.assertRaises(AssertionError, self.assertListEqual, None, b)
    self.assertRaises(AssertionError, self.assertTupleEqual, None, tuple(b))
    self.assertRaises(AssertionError, self.assertSequenceEqual, None, tuple(b))
    self.assertRaises(AssertionError, self.assertListEqual, 1, 1)
    self.assertRaises(AssertionError, self.assertTupleEqual, 1, 1)
    self.assertRaises(AssertionError, self.assertSequenceEqual, 1, 1)

    self.assertSameElements([1, 2, 3], [3, 2, 1])
    self.assertSameElements([1, 2] + [3] * 100, [1] * 100 + [2, 3])
    self.assertSameElements(['foo', 'bar', 'baz'], ['bar', 'baz', 'foo'])
    self.assertRaises(AssertionError, self.assertSameElements, [10], [10, 11])
    self.assertRaises(AssertionError, self.assertSameElements, [10, 11], [10])

    # Test that sequences of unhashable objects can be tested for sameness:
    self.assertSameElements([[1, 2], [3, 4]], [[3, 4], [1, 2]])
    self.assertRaises(AssertionError, self.assertSameElements, [[1]], [[2]])

  def test_assert_items_equal_hotfix(self):
    """Confirm that http://bugs.python.org/issue14832 - b/10038517 is gone."""
    for assert_items_method in (self.assertItemsEqual, self.assertCountEqual):
      with self.assertRaises(self.failureException) as error_context:
        assert_items_method([4], [2])
      error_message = str(error_context.exception)
      # Confirm that the bug is either no longer present in Python or that our
      # assertItemsEqual patching version of the method in absltest.TestCase
      # doesn't get used.
      self.assertIn('First has 1, Second has 0:  4', error_message)
      self.assertIn('First has 0, Second has 1:  2', error_message)

  @parameterized.product(
      class1=[dict, TestMapping],
      class2=[dict, TestMapping],
  )
  def test_assert_mapping_equal(self, class1, class2):
    self.assertMappingEqual(class1(), class2())

    self.assertRaisesRegex(
        absltest.TestCase.failureException,
        r' [!][=] ',
        self.assertMappingEqual,
        class1(x=1),
        class2(),
        'These are unequal',
    )
    self.assertRaisesRegex(
        absltest.TestCase.failureException,
        r' [!][=] ',
        self.assertMappingEqual,
        class1(x=1, y=2),
        class2(x=1, y=3),
    )

    self.assertRaisesRegex(
        AssertionError,
        'should be a Mapping',
        self.assertMappingEqual,
        class1(),
        (),
    )
    self.assertRaisesRegex(
        AssertionError,
        'should be a Mapping',
        self.assertMappingEqual,
        (),
        class2(),
    )

  def test_assert_mapping_equal_mapping_type(self):
    d1 = dict(one=1, two=2)
    d2 = TestMapping(one=1, two=2)

    self.assertMappingEqual(d1, d2, mapping_type=Mapping)
    self.assertRaisesRegex(
        AssertionError,
        'b should be a dict, found type: TestMapping',
        self.assertMappingEqual,
        d1,
        d2,
        mapping_type=dict,
    )
    self.assertRaisesRegex(
        AssertionError,
        'a should be a TestMapping, found type: dict',
        self.assertMappingEqual,
        d1,
        d2,
        mapping_type=TestMapping,
    )

  def test_assert_dict_equal_requires_dict(self):
    self.assertDictEqual(dict(one=1, two=2), dict(one=1, two=2))

    self.assertRaisesRegex(
        AssertionError,
        'should be a dict',
        self.assertDictEqual,
        dict(one=1, two=2),
        TestMapping(one=1, two=2),
    )
    self.assertRaisesRegex(
        AssertionError,
        'should be a dict',
        self.assertDictEqual,
        TestMapping(one=1, two=2),
        dict(one=1, two=2),
    )
    self.assertRaisesRegex(
        AssertionError,
        'should be a dict',
        self.assertDictEqual,
        TestMapping(one=1, two=2),
        TestMapping(one=1, two=2),
    )

  @parameterized.named_parameters(
      dict(testcase_name='dict', use_mapping=False),
      dict(testcase_name='mapping', use_mapping=True),
  )
  def test_assert_dict_equal(self, use_mapping: bool):

    def assert_dict_equal(a, b, msg=None, places=None, delta=None):
      if use_mapping:
        self.assertMappingEqual(a, b, msg=msg)
      elif places is None and delta is None:
        self.assertDictEqual(a, b, msg=msg)
      else:
        self.assertDictAlmostEqual(a, b, msg=msg, places=places, delta=delta)

    assert_dict_equal({}, {})

    c = {'x': 1}
    d: dict[str, int] = {}
    self.assertRaises(
        absltest.TestCase.failureException, assert_dict_equal, c, d
    )

    d.update(c)
    assert_dict_equal(c, d)

    d['x'] = 0
    self.assertRaises(
        absltest.TestCase.failureException,
        assert_dict_equal,
        c,
        d,
        'These are unequal',
    )

    self.assertRaises(AssertionError, assert_dict_equal, None, d)
    self.assertRaises(AssertionError, assert_dict_equal, [], d)
    self.assertRaises(AssertionError, assert_dict_equal, 1, 1)

    try:
      # Ensure we use equality as the sole measure of elements, not type, since
      # that is consistent with dict equality.
      assert_dict_equal({1: 1.0, 2: 2}, {1: 1, 2: 3})
    except AssertionError as e:
      self.assertMultiLineEqual('{1: 1.0, 2: 2} != {1: 1, 2: 3}\n'
                                'repr() of differing entries:\n2: 2 != 3\n',
                                str(e))

    try:
      assert_dict_equal({}, {'x': 1})
    except AssertionError as e:
      self.assertMultiLineEqual("{} != {'x': 1}\n"
                                "Unexpected, but present entries:\n'x': 1\n",
                                str(e))
    else:
      self.fail('Expecting AssertionError')

    try:
      assert_dict_equal({}, {'x': 1}, 'a message')
    except AssertionError as e:
      self.assertIn('a message', str(e))
    else:
      self.fail('Expecting AssertionError')

    expected = {'a': 1, 'b': 2, 'c': 3}
    seen = {'a': 2, 'c': 3, 'd': 4}
    try:
      assert_dict_equal(expected, seen)
    except AssertionError as e:
      self.assertMultiLineEqual(
          """\
{'a': 1, 'b': 2, 'c': 3} != {'a': 2, 'c': 3, 'd': 4}
Unexpected, but present entries:
'd': 4

repr() of differing entries:
'a': 1 != 2

Missing entries:
'b': 2
""",
          str(e),
      )
    else:
      self.fail('Expecting AssertionError')

    self.assertRaises(AssertionError, assert_dict_equal, (1, 2), {})
    self.assertRaises(AssertionError, assert_dict_equal, {}, (1, 2))

    # Ensure deterministic output of keys in dictionaries whose sort order
    # doesn't match the lexical ordering of repr -- this is most Python objects,
    # which are keyed by memory address.
    class Obj:

      def __init__(self, name):
        self.name = name

      def __repr__(self):
        return self.name

    try:
      assert_dict_equal(
          {'a': Obj('A'), Obj('b'): Obj('B'), Obj('c'): Obj('C')},
          {'a': Obj('A'), Obj('d'): Obj('D'), Obj('e'): Obj('E')},
      )
    except AssertionError as e:
      # Do as best we can not to be misleading when objects have the same repr
      # but aren't equal.
      err_str = str(e)
      self.assertStartsWith(err_str,
                            "{'a': A, b: B, c: C} != {'a': A, d: D, e: E}\n")
      self.assertRegex(
          err_str, r'(?ms).*^Unexpected, but present entries:\s+'
          r'^(d: D$\s+^e: E|e: E$\s+^d: D)$')
      self.assertRegex(
          err_str, r'(?ms).*^repr\(\) of differing entries:\s+'
          r'^.a.: A != A$', err_str)
      self.assertRegex(
          err_str, r'(?ms).*^Missing entries:\s+'
          r'^(b: B$\s+^c: C|c: C$\s+^b: B)$')
    else:
      self.fail('Expecting AssertionError')

    # Confirm that safe_repr, not repr, is being used.
    class RaisesOnRepr:

      def __repr__(self):
        return 1/0  # Intentionally broken __repr__ implementation.

    try:
      assert_dict_equal(
          {RaisesOnRepr(): RaisesOnRepr()},
          {RaisesOnRepr(): RaisesOnRepr()},
      )
      self.fail('Expected dicts not to match')
    except AssertionError as e:
      # Depending on the testing environment, the object may get a __main__
      # prefix or a absltest_test prefix, so strip that for comparison.
      error_msg = re.sub(
          r'( at 0x[^>]+)|__main__\.|absltest_test\.', '', str(e))
      self.assertRegex(error_msg, """(?m)\
{<.*RaisesOnRepr object.*>: <.*RaisesOnRepr object.*>} != \
{<.*RaisesOnRepr object.*>: <.*RaisesOnRepr object.*>}
Unexpected, but present entries:
<.*RaisesOnRepr object.*>: <.*RaisesOnRepr object.*>

Missing entries:
<.*RaisesOnRepr object.*>: <.*RaisesOnRepr object.*>
""")

    # Confirm that safe_repr, not repr, is being used.
    class RaisesOnLt:

      def __lt__(self, unused_other):
        raise TypeError('Object is unordered.')

      def __repr__(self):
        return '<RaisesOnLt object>'

    try:
      assert_dict_equal(
          {RaisesOnLt(): RaisesOnLt()},
          {RaisesOnLt(): RaisesOnLt()},
      )
    except AssertionError as e:
      self.assertIn('Unexpected, but present entries:\n<RaisesOnLt', str(e))
      self.assertIn('Missing entries:\n<RaisesOnLt', str(e))

  def test_assert_set_equal(self):
    set1 = set()
    set2 = set()
    self.assertSetEqual(set1, set2)

    self.assertRaises(AssertionError, self.assertSetEqual, None, set2)
    self.assertRaises(AssertionError, self.assertSetEqual, [], set2)
    self.assertRaises(AssertionError, self.assertSetEqual, set1, None)
    self.assertRaises(AssertionError, self.assertSetEqual, set1, [])

    set1 = {'a'}
    set2 = set()
    self.assertRaises(AssertionError, self.assertSetEqual, set1, set2)

    set1 = {'a'}
    set2 = {'a'}
    self.assertSetEqual(set1, set2)

    set1 = {'a'}
    set2 = {'a', 'b'}
    self.assertRaises(AssertionError, self.assertSetEqual, set1, set2)

    set1 = {'a'}
    set2 = frozenset(['a', 'b'])
    self.assertRaises(AssertionError, self.assertSetEqual, set1, set2)

    set1 = {'a', 'b'}
    set2 = frozenset(['a', 'b'])
    self.assertSetEqual(set1, set2)

    set1 = set()
    set2 = 'foo'
    self.assertRaises(AssertionError, self.assertSetEqual, set1, set2)
    self.assertRaises(AssertionError, self.assertSetEqual, set2, set1)

    # make sure any string formatting is tuple-safe
    set1 = {(0, 1), (2, 3)}
    set2 = {(4, 5)}
    self.assertRaises(AssertionError, self.assertSetEqual, set1, set2)

  @parameterized.named_parameters(
      dict(testcase_name='empty', a={}, b={}),
      dict(testcase_name='equal_float', a={'a': 1.01}, b={'a': 1.01}),
      dict(testcase_name='int_and_float', a={'a': 0}, b={'a': 0.000_000_01}),
      dict(testcase_name='float_and_int', a={'a': 0.000_000_01}, b={'a': 0}),
      dict(
          testcase_name='mixed_elements',
          a={'a': 'A', 'b': 1, 'c': 0.999_999_99},
          b={'a': 'A', 'b': 1, 'c': 1},
      ),
      dict(
          testcase_name='float_artifacts',
          a={'a': 0.15000000000000002},
          b={'a': 0.15},
      ),
      dict(
          testcase_name='multiple_floats',
          a={'a': 1.0, 'b': 2.0},
          b={'a': 1.000_000_01, 'b': 1.999_999_99},
      ),
  )
  def test_assert_dict_almost_equal(self, a, b):
    self.assertDictAlmostEqual(a, b)

  @parameterized.named_parameters(
      dict(
          testcase_name='default_places_is_7',
          a={'a': 1.0},
          b={'a': 1.000_000_01},
          places=None,
          delta=None,
      ),
      dict(
          testcase_name='places',
          a={'a': 1.011},
          b={'a': 1.009},
          places=2,
          delta=None,
      ),
      dict(
          testcase_name='delta',
          a={'a': 1.00},
          b={'a': 1.09},
          places=None,
          delta=0.1,
      ),
  )
  def test_assert_dict_almost_equal_with_tolerance(self, a, b, places, delta):
    self.assertDictAlmostEqual(a, b, places=places, delta=delta)

  @parameterized.named_parameters(
      dict(
          testcase_name='default_places_is_7',
          a={'a': 1.0},
          b={'a': 1.000_000_1},
          places=None,
          delta=None,
      ),
      dict(
          testcase_name='places',
          a={'a': 1.001},
          b={'a': 1.002},
          places=3,
          delta=None,
      ),
      dict(
          testcase_name='delta',
          a={'a': 1.01},
          b={'a': 1.02},
          places=None,
          delta=0.01,
      ),
  )
  def test_assert_dict_almost_equal_fails_with_tolerance(
      self, a, b, places, delta
  ):
    with self.assertRaises(self.failureException):
      self.assertDictAlmostEqual(a, b, places=places, delta=delta)

  def test_assert_dict_almost_equal_assertion_message(self):
    with self.assertRaises(AssertionError) as e:
      self.assertDictAlmostEqual({'a': 0.6}, {'a': 1.0}, delta=0.1)
    self.assertMultiLineEqual(
        """\
{'a': 0.6} != {'a': 1.0}
repr() of differing entries:
'a': 0.6 != 1.0 within 0.1 delta (0.4 difference)
""",
        str(e.exception),
    )

  def test_assert_dict_almost_equal_fails_with_custom_message(self):
    with self.assertRaises(AssertionError) as e:
      self.assertDictAlmostEqual(
          {'a': 0.6}, {'a': 1.0}, delta=0.1, msg='custom message'
      )
    self.assertMultiLineEqual(
        """\
{'a': 0.6} != {'a': 1.0}(custom message)
repr() of differing entries:
'a': 0.6 != 1.0 within 0.1 delta (0.4 difference)
""",
        str(e.exception),
    )

  def test_assert_dict_almost_equal_fails_with_both_places_and_delta(self):
    with self.assertRaises(ValueError) as e:
      self.assertDictAlmostEqual({'a': 1.0}, {'a': 1.0}, places=2, delta=0.01)
    self.assertMultiLineEqual(
        """\
specify delta or places not both
""",
        str(e.exception),
    )

  def test_assert_sequence_almost_equal(self):
    actual = (1.1, 1.2, 1.4)

    # Test across sequence types.
    self.assertSequenceAlmostEqual((1.1, 1.2, 1.4), actual)
    self.assertSequenceAlmostEqual([1.1, 1.2, 1.4], actual)

    # Test sequence size mismatch.
    with self.assertRaises(AssertionError):
      self.assertSequenceAlmostEqual([1.1, 1.2], actual)
    with self.assertRaises(AssertionError):
      self.assertSequenceAlmostEqual([1.1, 1.2, 1.4, 1.5], actual)

    # Test delta.
    with self.assertRaises(AssertionError):
      self.assertSequenceAlmostEqual((1.15, 1.15, 1.4), actual)
    self.assertSequenceAlmostEqual((1.15, 1.15, 1.4), actual, delta=0.1)

    # Test places.
    with self.assertRaises(AssertionError):
      self.assertSequenceAlmostEqual((1.1001, 1.2001, 1.3999), actual)
    self.assertSequenceAlmostEqual((1.1001, 1.2001, 1.3999), actual, places=3)

  def test_assert_contains_subset(self):
    # sets, lists, tuples, dicts all ok.  Types of set and subset do not have to
    # match.
    actual = ('a', 'b', 'c')
    self.assertContainsSubset({'a', 'b'}, actual)
    self.assertContainsSubset(('b', 'c'), actual)
    self.assertContainsSubset({'b': 1, 'c': 2}, list(actual))
    self.assertContainsSubset(['c', 'a'], set(actual))
    self.assertContainsSubset([], set())
    self.assertContainsSubset([], {'a': 1})

    self.assertRaises(AssertionError, self.assertContainsSubset, ('d',), actual)
    self.assertRaises(AssertionError, self.assertContainsSubset, ['d'],
                      set(actual))
    self.assertRaises(AssertionError, self.assertContainsSubset, {'a': 1}, [])

    with self.assertRaisesRegex(AssertionError, 'Missing elements'):
      self.assertContainsSubset({1, 2, 3}, {1, 2})

    with self.assertRaisesRegex(
        AssertionError,
        re.compile('Missing elements .* Custom message', re.DOTALL)):
      self.assertContainsSubset({1, 2}, {1}, 'Custom message')

  def test_assert_no_common_elements(self):
    actual = ('a', 'b', 'c')
    self.assertNoCommonElements((), actual)
    self.assertNoCommonElements(('d', 'e'), actual)
    self.assertNoCommonElements({'d', 'e'}, actual)

    with self.assertRaisesRegex(
        AssertionError,
        re.compile('Common elements .* Custom message', re.DOTALL)):
      self.assertNoCommonElements({1, 2}, {1}, 'Custom message')

    with self.assertRaises(AssertionError):
      self.assertNoCommonElements(['a'], actual)

    with self.assertRaises(AssertionError):
      self.assertNoCommonElements({'a', 'b', 'c'}, actual)

    with self.assertRaises(AssertionError):
      self.assertNoCommonElements({'b', 'c'}, set(actual))

  def test_assert_almost_equal(self):
    self.assertAlmostEqual(1.00000001, 1.0)
    self.assertNotAlmostEqual(1.0000001, 1.0)

  def test_assert_almost_equals_with_delta(self):
    self.assertAlmostEqual(3.14, 3, delta=0.2)
    self.assertAlmostEqual(2.81, 3.14, delta=1)
    self.assertAlmostEqual(-1, 1, delta=3)
    self.assertRaises(AssertionError, self.assertAlmostEqual,
                      3.14, 2.81, delta=0.1)
    self.assertRaises(AssertionError, self.assertAlmostEqual,
                      1, 2, delta=0.5)
    self.assertNotAlmostEqual(3.14, 2.81, delta=0.1)

  def test_assert_starts_with(self):
    self.assertStartsWith('foobar', 'foo')
    self.assertStartsWith('foobar', 'foobar')
    msg = 'This is a useful message'
    whole_msg = "'foobar' does not start with 'bar' : This is a useful message"
    self.assertRaisesWithLiteralMatch(AssertionError, whole_msg,
                                      self.assertStartsWith,
                                      'foobar', 'bar', msg)
    self.assertRaises(AssertionError, self.assertStartsWith, 'foobar', 'blah')

  def test_assert_not_starts_with(self):
    self.assertNotStartsWith('foobar', 'bar')
    self.assertNotStartsWith('foobar', 'blah')
    msg = 'This is a useful message'
    whole_msg = "'foobar' does start with 'foo' : This is a useful message"
    self.assertRaisesWithLiteralMatch(AssertionError, whole_msg,
                                      self.assertNotStartsWith,
                                      'foobar', 'foo', msg)
    self.assertRaises(AssertionError, self.assertNotStartsWith, 'foobar',
                      'foobar')

  def test_assert_ends_with(self):
    self.assertEndsWith('foobar', 'bar')
    self.assertEndsWith('foobar', 'foobar')
    msg = 'This is a useful message'
    whole_msg = "'foobar' does not end with 'foo' : This is a useful message"
    self.assertRaisesWithLiteralMatch(AssertionError, whole_msg,
                                      self.assertEndsWith,
                                      'foobar', 'foo', msg)
    self.assertRaises(AssertionError, self.assertEndsWith, 'foobar', 'blah')

  def test_assert_not_ends_with(self):
    self.assertNotEndsWith('foobar', 'foo')
    self.assertNotEndsWith('foobar', 'blah')
    msg = 'This is a useful message'
    whole_msg = "'foobar' does end with 'bar' : This is a useful message"
    self.assertRaisesWithLiteralMatch(AssertionError, whole_msg,
                                      self.assertNotEndsWith,
                                      'foobar', 'bar', msg)
    self.assertRaises(AssertionError, self.assertNotEndsWith, 'foobar',
                      'foobar')

  def test_assert_regex_backports(self):
    self.assertRegex('regex', 'regex')
    self.assertNotRegex('not-regex', 'no-match')
    with self.assertRaisesRegex(ValueError, 'pattern'):
      raise ValueError('pattern')

  def test_assert_regex_match_matches(self):
    self.assertRegexMatch('str', ['str'])

  def test_assert_regex_match_matches_substring(self):
    self.assertRegexMatch('pre-str-post', ['str'])

  def test_assert_regex_match_multiple_regex_matches(self):
    self.assertRegexMatch('str', ['rts', 'str'])

  def test_assert_regex_match_empty_list_fails(self):
    expected_re = re.compile(r'No regexes specified\.', re.MULTILINE)

    with self.assertRaisesRegex(AssertionError, expected_re):
      self.assertRegexMatch('str', regexes=[])

  def test_assert_regex_match_bad_arguments(self):
    with self.assertRaisesRegex(AssertionError,
                                'regexes is string or bytes;.*'):
      self.assertRegexMatch('1.*2', '1 2')

  def test_assert_regex_match_unicode_vs_bytes(self):
    """Ensure proper utf-8 encoding or decoding happens automatically."""
    self.assertRegexMatch('str', [b'str'])
    self.assertRegexMatch(b'str', ['str'])

  def test_assert_regex_match_unicode(self):
    self.assertRegexMatch('foo str', ['str'])

  def test_assert_regex_match_bytes(self):
    self.assertRegexMatch(b'foo str', [b'str'])

  def test_assert_regex_match_all_the_same_type(self):
    with self.assertRaisesRegex(AssertionError, 'regexes .* same type'):
      self.assertRegexMatch('foo str', [b'str', 'foo'])

  def test_assert_command_fails_stderr(self):
    tmpdir = tempfile.mkdtemp(dir=absltest.TEST_TMPDIR.value)
    self.assertCommandFails(
        ['cat', os.path.join(tmpdir, 'file.txt')],
        ['No such file or directory'],
        env=_env_for_command_tests())

  def test_assert_command_fails_with_list_of_string(self):
    self.assertCommandFails(
        ['false'], [''], env=_env_for_command_tests())

  def test_assert_command_fails_with_list_of_unicode_string(self):
    self.assertCommandFails(['false'], [''], env=_env_for_command_tests())

  def test_assert_command_fails_with_unicode_string(self):
    self.assertCommandFails('false', [''], env=_env_for_command_tests())

  def test_assert_command_fails_with_unicode_string_bytes_regex(self):
    self.assertCommandFails('false', [b''], env=_env_for_command_tests())

  def test_assert_command_fails_with_message(self):
    msg = 'This is a useful message'
    expected_re = re.compile('The following command succeeded while expected to'
                             ' fail:.* This is a useful message', re.DOTALL)

    with self.assertRaisesRegex(AssertionError, expected_re):
      self.assertCommandFails(
          ['true'], [''], msg=msg, env=_env_for_command_tests()
      )

  def test_assert_command_succeeds_stderr(self):
    expected_re = re.compile('No such file or directory')
    tmpdir = tempfile.mkdtemp(dir=absltest.TEST_TMPDIR.value)

    with self.assertRaisesRegex(AssertionError, expected_re):
      self.assertCommandSucceeds(
          ['cat', os.path.join(tmpdir, 'file.txt')],
          env=_env_for_command_tests())

  def test_assert_command_succeeds_with_matching_unicode_regexes(self):
    self.assertCommandSucceeds(
        ['echo', 'SUCCESS'], regexes=['SUCCESS'], env=_env_for_command_tests()
    )

  def test_assert_command_succeeds_with_matching_bytes_regexes(self):
    self.assertCommandSucceeds(
        ['echo', 'SUCCESS'], regexes=[b'SUCCESS'],
        env=_env_for_command_tests())

  def test_assert_command_succeeds_with_non_matching_regexes(self):
    expected_re = re.compile('Running command.* This is a useful message',
                             re.DOTALL)
    msg = 'This is a useful message'

    with self.assertRaisesRegex(AssertionError, expected_re):
      self.assertCommandSucceeds(
          ['echo', 'FAIL'], regexes=['SUCCESS'], msg=msg,
          env=_env_for_command_tests())

  def test_assert_command_succeeds_with_list_of_string(self):
    self.assertCommandSucceeds(
        ['true'], env=_env_for_command_tests())

  def test_assert_command_succeeds_with_list_of_unicode_string(self):
    self.assertCommandSucceeds(['true'], env=_env_for_command_tests())

  def test_assert_command_succeeds_with_unicode_string(self):
    self.assertCommandSucceeds('true', env=_env_for_command_tests())

  def test_inequality(self):
    # Try ints
    self.assertGreater(2, 1)
    self.assertGreaterEqual(2, 1)
    self.assertGreaterEqual(1, 1)
    self.assertLess(1, 2)
    self.assertLessEqual(1, 2)
    self.assertLessEqual(1, 1)
    self.assertRaises(AssertionError, self.assertGreater, 1, 2)
    self.assertRaises(AssertionError, self.assertGreater, 1, 1)
    self.assertRaises(AssertionError, self.assertGreaterEqual, 1, 2)
    self.assertRaises(AssertionError, self.assertLess, 2, 1)
    self.assertRaises(AssertionError, self.assertLess, 1, 1)
    self.assertRaises(AssertionError, self.assertLessEqual, 2, 1)

    # Try Floats
    self.assertGreater(1.1, 1.0)
    self.assertGreaterEqual(1.1, 1.0)
    self.assertGreaterEqual(1.0, 1.0)
    self.assertLess(1.0, 1.1)
    self.assertLessEqual(1.0, 1.1)
    self.assertLessEqual(1.0, 1.0)
    self.assertRaises(AssertionError, self.assertGreater, 1.0, 1.1)
    self.assertRaises(AssertionError, self.assertGreater, 1.0, 1.0)
    self.assertRaises(AssertionError, self.assertGreaterEqual, 1.0, 1.1)
    self.assertRaises(AssertionError, self.assertLess, 1.1, 1.0)
    self.assertRaises(AssertionError, self.assertLess, 1.0, 1.0)
    self.assertRaises(AssertionError, self.assertLessEqual, 1.1, 1.0)

    # Try Strings
    self.assertGreater('bug', 'ant')
    self.assertGreaterEqual('bug', 'ant')
    self.assertGreaterEqual('ant', 'ant')
    self.assertLess('ant', 'bug')
    self.assertLessEqual('ant', 'bug')
    self.assertLessEqual('ant', 'ant')
    self.assertRaises(AssertionError, self.assertGreater, 'ant', 'bug')
    self.assertRaises(AssertionError, self.assertGreater, 'ant', 'ant')
    self.assertRaises(AssertionError, self.assertGreaterEqual, 'ant', 'bug')
    self.assertRaises(AssertionError, self.assertLess, 'bug', 'ant')
    self.assertRaises(AssertionError, self.assertLess, 'ant', 'ant')
    self.assertRaises(AssertionError, self.assertLessEqual, 'bug', 'ant')

    # Try Unicode
    self.assertGreater('bug', 'ant')
    self.assertGreaterEqual('bug', 'ant')
    self.assertGreaterEqual('ant', 'ant')
    self.assertLess('ant', 'bug')
    self.assertLessEqual('ant', 'bug')
    self.assertLessEqual('ant', 'ant')
    self.assertRaises(AssertionError, self.assertGreater, 'ant', 'bug')
    self.assertRaises(AssertionError, self.assertGreater, 'ant', 'ant')
    self.assertRaises(AssertionError, self.assertGreaterEqual, 'ant', 'bug')
    self.assertRaises(AssertionError, self.assertLess, 'bug', 'ant')
    self.assertRaises(AssertionError, self.assertLess, 'ant', 'ant')
    self.assertRaises(AssertionError, self.assertLessEqual, 'bug', 'ant')

    # Try Mixed String/Unicode
    self.assertGreater('bug', 'ant')
    self.assertGreater('bug', 'ant')
    self.assertGreaterEqual('bug', 'ant')
    self.assertGreaterEqual('bug', 'ant')
    self.assertGreaterEqual('ant', 'ant')
    self.assertGreaterEqual('ant', 'ant')
    self.assertLess('ant', 'bug')
    self.assertLess('ant', 'bug')
    self.assertLessEqual('ant', 'bug')
    self.assertLessEqual('ant', 'bug')
    self.assertLessEqual('ant', 'ant')
    self.assertLessEqual('ant', 'ant')
    self.assertRaises(AssertionError, self.assertGreater, 'ant', 'bug')
    self.assertRaises(AssertionError, self.assertGreater, 'ant', 'bug')
    self.assertRaises(AssertionError, self.assertGreater, 'ant', 'ant')
    self.assertRaises(AssertionError, self.assertGreater, 'ant', 'ant')
    self.assertRaises(AssertionError, self.assertGreaterEqual, 'ant', 'bug')
    self.assertRaises(AssertionError, self.assertGreaterEqual, 'ant', 'bug')
    self.assertRaises(AssertionError, self.assertLess, 'bug', 'ant')
    self.assertRaises(AssertionError, self.assertLess, 'bug', 'ant')
    self.assertRaises(AssertionError, self.assertLess, 'ant', 'ant')
    self.assertRaises(AssertionError, self.assertLess, 'ant', 'ant')
    self.assertRaises(AssertionError, self.assertLessEqual, 'bug', 'ant')
    self.assertRaises(AssertionError, self.assertLessEqual, 'bug', 'ant')

  def test_assert_multi_line_equal(self):
    sample_text = """\
http://www.python.org/doc/2.3/lib/module-unittest.html
test case
    A test case is the smallest unit of testing. [...]
"""
    revised_sample_text = """\
http://www.python.org/doc/2.4.1/lib/module-unittest.html
test case
    A test case is the smallest unit of testing. [...] You may provide your
    own implementation that does not subclass from TestCase, of course.
"""
    sample_text_error = """
- http://www.python.org/doc/2.3/lib/module-unittest.html
?                             ^
+ http://www.python.org/doc/2.4.1/lib/module-unittest.html
?                             ^^^
  test case
-     A test case is the smallest unit of testing. [...]
+     A test case is the smallest unit of testing. [...] You may provide your
?                                                       +++++++++++++++++++++
+     own implementation that does not subclass from TestCase, of course.
"""
    self.assertRaisesWithLiteralMatch(AssertionError, sample_text_error,
                                      self.assertMultiLineEqual,
                                      sample_text,
                                      revised_sample_text)

    self.assertRaises(AssertionError, self.assertMultiLineEqual, (1, 2), 'str')
    self.assertRaises(AssertionError, self.assertMultiLineEqual, 'str', (1, 2))

  def test_assert_multi_line_equal_adds_newlines_if_needed(self):
    self.assertRaisesWithLiteralMatch(
        AssertionError,
        '\n'
        '  line1\n'
        '- line2\n'
        '?     ^\n'
        '+ line3\n'
        '?     ^\n',
        self.assertMultiLineEqual,
        'line1\n'
        'line2',
        'line1\n'
        'line3')

  def test_assert_multi_line_equal_shows_missing_newlines(self):
    self.assertRaisesWithLiteralMatch(
        AssertionError,
        '\n'
        '  line1\n'
        '- line2\n'
        '?      -\n'
        '+ line2\n',
        self.assertMultiLineEqual,
        'line1\n'
        'line2\n',
        'line1\n'
        'line2')

  def test_assert_multi_line_equal_shows_extra_newlines(self):
    self.assertRaisesWithLiteralMatch(
        AssertionError,
        '\n'
        '  line1\n'
        '- line2\n'
        '+ line2\n'
        '?      +\n',
        self.assertMultiLineEqual,
        'line1\n'
        'line2',
        'line1\n'
        'line2\n')

  def test_assert_multi_line_equal_line_limit_limits(self):
    self.assertRaisesWithLiteralMatch(
        AssertionError,
        '\n'
        '  line1\n'
        '(... and 4 more delta lines omitted for brevity.)\n',
        self.assertMultiLineEqual,
        'line1\n'
        'line2\n',
        'line1\n'
        'line3\n',
        line_limit=1)

  def test_assert_multi_line_equal_line_limit_limits_with_message(self):
    self.assertRaisesWithLiteralMatch(
        AssertionError,
        'Prefix:\n'
        '  line1\n'
        '(... and 4 more delta lines omitted for brevity.)\n',
        self.assertMultiLineEqual,
        'line1\n'
        'line2\n',
        'line1\n'
        'line3\n',
        'Prefix',
        line_limit=1)

  def test_assert_is_none(self):
    self.assertIsNone(None)
    self.assertRaises(AssertionError, self.assertIsNone, False)
    self.assertIsNotNone('Google')
    self.assertRaises(AssertionError, self.assertIsNotNone, None)
    self.assertRaises(AssertionError, self.assertIsNone, (1, 2))

  def test_assert_is(self):
    self.assertIs(object, object)
    self.assertRaises(AssertionError, self.assertIsNot, object, object)
    self.assertIsNot(True, False)
    self.assertRaises(AssertionError, self.assertIs, True, False)

  def test_assert_between(self):
    self.assertBetween(3.14, 3.1, 3.141)
    self.assertBetween(4, 4, 1e10000)
    self.assertBetween(9.5, 9.4, 9.5)
    self.assertBetween(-1e10, -1e10000, 0)
    self.assertRaises(AssertionError, self.assertBetween, 9.4, 9.3, 9.3999)
    self.assertRaises(AssertionError, self.assertBetween, -1e10000, -1e10, 0)

  def test_assert_raises_with_predicate_match_no_raise(self):
    with self.assertRaisesRegex(AssertionError, '^Exception not raised$'):
      self.assertRaisesWithPredicateMatch(Exception,
                                          lambda e: True,
                                          lambda: 1)  # don't raise

    with self.assertRaisesRegex(AssertionError, '^Exception not raised$'):
      with self.assertRaisesWithPredicateMatch(Exception, lambda e: True):
        pass  # don't raise

  def test_assert_raises_with_predicate_match_raises_wrong_exception(self):
    def _raise_value_error():
      raise ValueError

    with self.assertRaises(ValueError):
      self.assertRaisesWithPredicateMatch(IOError,
                                          lambda e: True,
                                          _raise_value_error)

    with self.assertRaises(ValueError):
      with self.assertRaisesWithPredicateMatch(IOError, lambda e: True):
        raise ValueError

  def test_assert_raises_with_predicate_match_predicate_fails(self):
    def _raise_value_error():
      raise ValueError
    with self.assertRaisesRegex(AssertionError, ' does not match predicate '):
      self.assertRaisesWithPredicateMatch(ValueError,
                                          lambda e: False,
                                          _raise_value_error)

    with self.assertRaisesRegex(AssertionError, ' does not match predicate '):
      with self.assertRaisesWithPredicateMatch(ValueError, lambda e: False):
        raise ValueError

  def test_assert_raises_with_predicate_match_predicate_passes(self):
    def _raise_value_error():
      raise ValueError

    self.assertRaisesWithPredicateMatch(ValueError,
                                        lambda e: True,
                                        _raise_value_error)

    with self.assertRaisesWithPredicateMatch(ValueError, lambda e: True):
      raise ValueError

  def test_assert_raises_with_predicate_match_exception_captured(self):
    def _raise_value_error():
      raise ValueError

    predicate = lambda e: e is not None
    with self.assertRaisesWithPredicateMatch(ValueError, predicate) as ctx_mgr:
      _raise_value_error()

    expected = getattr(ctx_mgr, 'exception', None)
    self.assertIsInstance(expected, ValueError)

  def test_assert_raises_with_literal_match_exception_captured(self):
    message = 'some value error'
    def _raise_value_error():
      raise ValueError(message)

    # predicate = lambda e: e is not None
    with self.assertRaisesWithLiteralMatch(ValueError, message) as ctx_mgr:
      _raise_value_error()

    expected = getattr(ctx_mgr, 'exception', None)
    self.assertIsInstance(expected, ValueError)

  def test_assert_contains_in_order(self):
    # Valids
    self.assertContainsInOrder(
        ['fox', 'dog'], 'The quick brown fox jumped over the lazy dog.')
    self.assertContainsInOrder(
        ['quick', 'fox', 'dog'],
        'The quick brown fox jumped over the lazy dog.')
    self.assertContainsInOrder(
        ['The', 'fox', 'dog.'], 'The quick brown fox jumped over the lazy dog.')
    self.assertContainsInOrder(
        ['fox'], 'The quick brown fox jumped over the lazy dog.')
    self.assertContainsInOrder(
        'fox', 'The quick brown fox jumped over the lazy dog.')
    self.assertContainsInOrder(
        ['fox', 'dog'], 'fox dog fox')
    self.assertContainsInOrder(
        [], 'The quick brown fox jumped over the lazy dog.')
    self.assertContainsInOrder(
        [], '')

    # Invalids
    msg = 'This is a useful message'
    whole_msg = ("Did not find 'fox' after 'dog' in 'The quick brown fox"
                 " jumped over the lazy dog' : This is a useful message")
    self.assertRaisesWithLiteralMatch(
        AssertionError, whole_msg, self.assertContainsInOrder,
        ['dog', 'fox'], 'The quick brown fox jumped over the lazy dog', msg=msg)
    self.assertRaises(
        AssertionError, self.assertContainsInOrder,
        ['The', 'dog', 'fox'], 'The quick brown fox jumped over the lazy dog')
    self.assertRaises(
        AssertionError, self.assertContainsInOrder, ['dog'], '')

  def test_assert_contains_subsequence_for_numbers(self):
    self.assertContainsSubsequence([1, 2, 3], [1])
    self.assertContainsSubsequence([1, 2, 3], [1, 2])
    self.assertContainsSubsequence([1, 2, 3], [1, 3])

    with self.assertRaises(AssertionError):
      self.assertContainsSubsequence([1, 2, 3], [4])
    msg = 'This is a useful message'
    whole_msg = ('[3, 1] not a subsequence of [1, 2, 3]. '
                 'First non-matching element: 1 : This is a useful message')
    self.assertRaisesWithLiteralMatch(AssertionError, whole_msg,
                                      self.assertContainsSubsequence,
                                      [1, 2, 3], [3, 1], msg=msg)

  def test_assert_contains_subsequence_for_strings(self):
    self.assertContainsSubsequence(['foo', 'bar', 'blorp'], ['foo', 'blorp'])
    with self.assertRaises(AssertionError):
      self.assertContainsSubsequence(
          ['foo', 'bar', 'blorp'], ['blorp', 'foo'])

  def test_assert_contains_subsequence_with_empty_subsequence(self):
    self.assertContainsSubsequence([1, 2, 3], [])
    self.assertContainsSubsequence(['foo', 'bar', 'blorp'], [])
    self.assertContainsSubsequence([], [])

  def test_assert_contains_subsequence_with_empty_container(self):
    with self.assertRaises(AssertionError):
      self.assertContainsSubsequence([], [1])
    with self.assertRaises(AssertionError):
      self.assertContainsSubsequence([], ['foo'])

  def test_assert_contains_exact_subsequence_for_numbers(self):
    self.assertContainsExactSubsequence([1, 2, 3], [1])
    self.assertContainsExactSubsequence([1, 2, 3], [1, 2])
    self.assertContainsExactSubsequence([1, 2, 3], [2, 3])

    with self.assertRaises(AssertionError):
      self.assertContainsExactSubsequence([1, 2, 3], [4])
    msg = 'This is a useful message'
    whole_msg = ('[1, 2, 4] not an exact subsequence of [1, 2, 3, 4]. '
                 'Longest matching prefix: [1, 2] : This is a useful message')
    self.assertRaisesWithLiteralMatch(AssertionError, whole_msg,
                                      self.assertContainsExactSubsequence,
                                      [1, 2, 3, 4], [1, 2, 4], msg=msg)

  def test_assert_contains_exact_subsequence_for_strings(self):
    self.assertContainsExactSubsequence(
        ['foo', 'bar', 'blorp'], ['foo', 'bar'])
    with self.assertRaises(AssertionError):
      self.assertContainsExactSubsequence(
          ['foo', 'bar', 'blorp'], ['blorp', 'foo'])

  def test_assert_contains_exact_subsequence_with_empty_subsequence(self):
    self.assertContainsExactSubsequence([1, 2, 3], [])
    self.assertContainsExactSubsequence(['foo', 'bar', 'blorp'], [])
    self.assertContainsExactSubsequence([], [])

  def test_assert_contains_exact_subsequence_with_empty_container(self):
    with self.assertRaises(AssertionError):
      self.assertContainsExactSubsequence([], [3])
    with self.assertRaises(AssertionError):
      self.assertContainsExactSubsequence([], ['foo', 'bar'])
    self.assertContainsExactSubsequence([], [])

  def test_assert_totally_ordered(self):
    # Valid.
    self.assertTotallyOrdered()
    self.assertTotallyOrdered([1])
    self.assertTotallyOrdered([1], [2])
    self.assertTotallyOrdered([1, 1, 1])
    self.assertTotallyOrdered([(1, 1)], [(1, 2)], [(2, 1)])

    # From the docstring.
    class A:

      def __init__(self, x, y):
        self.x = x
        self.y = y

      def __hash__(self):
        return hash(self.x)

      def __repr__(self):
        return 'A(%r, %r)' % (self.x, self.y)

      def __eq__(self, other):
        try:
          return self.x == other.x
        except AttributeError:
          return NotImplemented

      def __ne__(self, other):
        try:
          return self.x != other.x
        except AttributeError:
          return NotImplemented

      def __lt__(self, other):
        try:
          return self.x < other.x
        except AttributeError:
          return NotImplemented

      def __le__(self, other):
        try:
          return self.x <= other.x
        except AttributeError:
          return NotImplemented

      def __gt__(self, other):
        try:
          return self.x > other.x
        except AttributeError:
          return NotImplemented

      def __ge__(self, other):
        try:
          return self.x >= other.x
        except AttributeError:
          return NotImplemented

    class B(A):
      """Like A, but not hashable."""
      __hash__ = None

    self.assertTotallyOrdered(
        [A(1, 'a')],
        [A(2, 'b')],  # 2 is after 1.
        [
            A(3, 'c'),
            B(3, 'd'),
            B(3, 'e')  # The second argument is irrelevant.
        ],
        [A(4, 'z')])

    # Invalid.
    msg = 'This is a useful message'
    whole_msg = '2 not less than 1 : This is a useful message'
    self.assertRaisesWithLiteralMatch(AssertionError, whole_msg,
                                      self.assertTotallyOrdered, [2], [1],
                                      msg=msg)
    self.assertRaises(AssertionError, self.assertTotallyOrdered, [2], [1])
    self.assertRaises(AssertionError, self.assertTotallyOrdered, [2], [1], [3])
    self.assertRaises(AssertionError, self.assertTotallyOrdered, [1, 2])

  def test_short_description_without_docstring(self):
    self.assertEqual(
        self.shortDescription(),
        'TestCaseTest.test_short_description_without_docstring',
    )

  def test_short_description_with_one_line_docstring(self):
    """Tests shortDescription() for a method with a docstring."""
    self.assertEqual(
        self.shortDescription(),
        'TestCaseTest.test_short_description_with_one_line_docstring\n'
        'Tests shortDescription() for a method with a docstring.',
    )

  def test_short_description_with_multi_line_docstring(self):
    """Tests shortDescription() for a method with a longer docstring.

    This method ensures that only the first line of a docstring is
    returned used in the short description, no matter how long the
    whole thing is.
    """
    self.assertEqual(
        self.shortDescription(),
        'TestCaseTest.test_short_description_with_multi_line_docstring\n'
        'Tests shortDescription() for a method with a longer docstring.',
    )

  def test_assert_url_equal_same(self):
    self.assertUrlEqual('http://a', 'http://a')
    self.assertUrlEqual('http://a/path/test', 'http://a/path/test')
    self.assertUrlEqual('#fragment', '#fragment')
    self.assertUrlEqual('http://a/?q=1', 'http://a/?q=1')
    self.assertUrlEqual('http://a/?q=1&v=5', 'http://a/?v=5&q=1')
    self.assertUrlEqual('/logs?v=1&a=2&t=labels&f=path%3A%22foo%22',
                        '/logs?a=2&f=path%3A%22foo%22&v=1&t=labels')
    self.assertUrlEqual('http://a/path;p1', 'http://a/path;p1')
    self.assertUrlEqual('http://a/path;p2;p3;p1', 'http://a/path;p1;p2;p3')
    self.assertUrlEqual('sip:alice@atlanta.com;maddr=239.255.255.1;ttl=15',
                        'sip:alice@atlanta.com;ttl=15;maddr=239.255.255.1')
    self.assertUrlEqual('http://nyan/cat?p=1&b=', 'http://nyan/cat?b=&p=1')

  def test_assert_url_equal_different(self):
    msg = 'This is a useful message'
    whole_msg = 'This is a useful message:\n- a\n+ b\n'
    self.assertRaisesWithLiteralMatch(AssertionError, whole_msg,
                                      self.assertUrlEqual,
                                      'http://a', 'http://b', msg=msg)
    self.assertRaises(AssertionError, self.assertUrlEqual,
                      'http://a/x', 'http://a:8080/x')
    self.assertRaises(AssertionError, self.assertUrlEqual,
                      'http://a/x', 'http://a/y')
    self.assertRaises(AssertionError, self.assertUrlEqual,
                      'http://a/?q=2', 'http://a/?q=1')
    self.assertRaises(AssertionError, self.assertUrlEqual,
                      'http://a/?q=1&v=5', 'http://a/?v=2&q=1')
    self.assertRaises(AssertionError, self.assertUrlEqual,
                      'http://a', 'sip://b')
    self.assertRaises(AssertionError, self.assertUrlEqual,
                      'http://a#g', 'sip://a#f')
    self.assertRaises(AssertionError, self.assertUrlEqual,
                      'http://a/path;p1;p3;p1', 'http://a/path;p1;p2;p3')
    self.assertRaises(AssertionError, self.assertUrlEqual,
                      'http://nyan/cat?p=1&b=', 'http://nyan/cat?p=1')

  def test_same_structure_same(self):
    self.assertSameStructure(0, 0)
    self.assertSameStructure(1, 1)
    self.assertSameStructure('', '')
    self.assertSameStructure('hello', 'hello', msg='This Should not fail')
    self.assertSameStructure(set(), set())
    self.assertSameStructure({1, 2}, {1, 2})
    self.assertSameStructure(set(), frozenset())
    self.assertSameStructure({1, 2}, frozenset([1, 2]))
    self.assertSameStructure([], [])
    self.assertSameStructure(['a'], ['a'])
    self.assertSameStructure([], ())
    self.assertSameStructure(['a'], ('a',))
    self.assertSameStructure({}, {})
    self.assertSameStructure({'one': 1}, {'one': 1})
    self.assertSameStructure(collections.defaultdict(None, {'one': 1}),
                             {'one': 1})
    self.assertSameStructure(collections.OrderedDict({'one': 1}),
                             collections.defaultdict(None, {'one': 1}))

  def test_same_structure_different(self):
    # Different type
    with self.assertRaisesRegex(
        AssertionError,
        r"a is a <(type|class) 'int'> but b is a <(type|class) 'str'>"):
      self.assertSameStructure(0, 'hello')
    with self.assertRaisesRegex(
        AssertionError,
        r"a is a <(type|class) 'int'> but b is a <(type|class) 'list'>"):
      self.assertSameStructure(0, [])
    with self.assertRaisesRegex(
        AssertionError,
        r"a is a <(type|class) 'int'> but b is a <(type|class) 'float'>"):
      self.assertSameStructure(2, 2.0)

    with self.assertRaisesRegex(
        AssertionError,
        r"a is a <(type|class) 'list'> but b is a <(type|class) 'dict'>"):
      self.assertSameStructure([], {})

    with self.assertRaisesRegex(
        AssertionError,
        r"a is a <(type|class) 'list'> but b is a <(type|class) 'set'>"):
      self.assertSameStructure([], set())

    with self.assertRaisesRegex(
        AssertionError,
        r"a is a <(type|class) 'dict'> but b is a <(type|class) 'set'>"):
      self.assertSameStructure({}, set())

    # Different scalar values
    self.assertRaisesWithLiteralMatch(
        AssertionError, 'a is 0 but b is 1',
        self.assertSameStructure, 0, 1)
    self.assertRaisesWithLiteralMatch(
        AssertionError, "a is 'hello' but b is 'goodbye' : This was expected",
        self.assertSameStructure, 'hello', 'goodbye', msg='This was expected')

    # Different sets
    self.assertRaisesWithLiteralMatch(
        AssertionError,
        r'AA has 2 but BB does not',
        self.assertSameStructure,
        {1, 2},
        {1},
        aname='AA',
        bname='BB',
    )
    self.assertRaisesWithLiteralMatch(
        AssertionError,
        r'AA lacks 2 but BB has it',
        self.assertSameStructure,
        {1},
        {1, 2},
        aname='AA',
        bname='BB',
    )

    # Different lists
    self.assertRaisesWithLiteralMatch(
        AssertionError, "a has [2] with value 'z' but b does not",
        self.assertSameStructure, ['x', 'y', 'z'], ['x', 'y'])
    self.assertRaisesWithLiteralMatch(
        AssertionError, "a lacks [2] but b has it with value 'z'",
        self.assertSameStructure, ['x', 'y'], ['x', 'y', 'z'])
    self.assertRaisesWithLiteralMatch(
        AssertionError, "a[2] is 'z' but b[2] is 'Z'",
        self.assertSameStructure, ['x', 'y', 'z'], ['x', 'y', 'Z'])

    # Different dicts
    self.assertRaisesWithLiteralMatch(
        AssertionError, "a has ['two'] with value 2 but it's missing in b",
        self.assertSameStructure, {'one': 1, 'two': 2}, {'one': 1})
    self.assertRaisesWithLiteralMatch(
        AssertionError, "a lacks ['two'] but b has it with value 2",
        self.assertSameStructure, {'one': 1}, {'one': 1, 'two': 2})
    self.assertRaisesWithLiteralMatch(
        AssertionError, "a['two'] is 2 but b['two'] is 3",
        self.assertSameStructure, {'one': 1, 'two': 2}, {'one': 1, 'two': 3})

    # String and byte types should not be considered equivalent to other
    # sequences
    self.assertRaisesRegex(
        AssertionError,
        r"a is a <(type|class) 'list'> but b is a <(type|class) 'str'>",
        self.assertSameStructure, [], '')
    self.assertRaisesRegex(
        AssertionError,
        r"a is a <(type|class) 'str'> but b is a <(type|class) 'tuple'>",
        self.assertSameStructure, '', ())
    self.assertRaisesRegex(
        AssertionError,
        r"a is a <(type|class) 'list'> but b is a <(type|class) 'str'>",
        self.assertSameStructure, ['a', 'b', 'c'], 'abc')
    self.assertRaisesRegex(
        AssertionError,
        r"a is a <(type|class) 'str'> but b is a <(type|class) 'tuple'>",
        self.assertSameStructure, 'abc', ('a', 'b', 'c'))

    # Deep key generation
    self.assertRaisesWithLiteralMatch(
        AssertionError,
        "a[0][0]['x']['y']['z'][0] is 1 but b[0][0]['x']['y']['z'][0] is 2",
        self.assertSameStructure,
        [[{'x': {'y': {'z': [1]}}}]], [[{'x': {'y': {'z': [2]}}}]])

    # Multiple problems
    self.assertRaisesWithLiteralMatch(
        AssertionError,
        'a[0] is 1 but b[0] is 3; a[1] is 2 but b[1] is 4',
        self.assertSameStructure, [1, 2], [3, 4])
    with self.assertRaisesRegex(
        AssertionError,
        re.compile(r"^a\[0] is 'a' but b\[0] is 'A'; .*"
                   r"a\[18] is 's' but b\[18] is 'S'; \.\.\.$")):
      self.assertSameStructure(
          list(string.ascii_lowercase), list(string.ascii_uppercase))

    # Verify same behavior with self.maxDiff = None
    self.maxDiff = None
    self.assertRaisesWithLiteralMatch(
        AssertionError,
        'a[0] is 1 but b[0] is 3; a[1] is 2 but b[1] is 4',
        self.assertSameStructure, [1, 2], [3, 4])

  def test_same_structure_mapping_unchanged(self):
    default_a = collections.defaultdict(lambda: 'BAD MODIFICATION', {})
    dict_b = {'one': 'z'}
    self.assertRaisesWithLiteralMatch(
        AssertionError,
        r"a lacks ['one'] but b has it with value 'z'",
        self.assertSameStructure, default_a, dict_b)
    self.assertEmpty(default_a)

    dict_a = {'one': 'z'}
    default_b = collections.defaultdict(lambda: 'BAD MODIFICATION', {})
    self.assertRaisesWithLiteralMatch(
        AssertionError,
        r"a has ['one'] with value 'z' but it's missing in b",
        self.assertSameStructure, dict_a, default_b)
    self.assertEmpty(default_b)

  def test_same_structure_uses_type_equality_func_for_leaves(self):

    class CustomLeaf:
      def __init__(self, n):
        self.n = n

      def __repr__(self):
        return f'CustomLeaf({self.n})'

    def assert_custom_leaf_equal(a, b, msg):
      del msg
      assert a.n % 5 == b.n % 5
    self.addTypeEqualityFunc(CustomLeaf, assert_custom_leaf_equal)

    self.assertSameStructure(CustomLeaf(4), CustomLeaf(9))
    self.assertRaisesWithLiteralMatch(
        AssertionError,
        r'a is CustomLeaf(4) but b is CustomLeaf(8)',
        self.assertSameStructure, CustomLeaf(4), CustomLeaf(8),
    )

  def test_assert_json_equal_same(self):
    self.assertJsonEqual('{"success": true}', '{"success": true}')
    self.assertJsonEqual('{"success": true}', '{"success":true}')
    self.assertJsonEqual('true', 'true')
    self.assertJsonEqual('null', 'null')
    self.assertJsonEqual('false', 'false')
    self.assertJsonEqual('34', '34')
    self.assertJsonEqual('[1, 2, 3]', '[1,2,3]', msg='please PASS')
    self.assertJsonEqual('{"sequence": [1, 2, 3], "float": 23.42}',
                         '{"float": 23.42, "sequence": [1,2,3]}')
    self.assertJsonEqual('{"nest": {"spam": "eggs"}, "float": 23.42}',
                         '{"float": 23.42, "nest": {"spam":"eggs"}}')

  def test_assert_json_equal_different(self):
    with self.assertRaises(AssertionError):
      self.assertJsonEqual('{"success": true}', '{"success": false}')
    with self.assertRaises(AssertionError):
      self.assertJsonEqual('{"success": false}', '{"Success": false}')
    with self.assertRaises(AssertionError):
      self.assertJsonEqual('false', 'true')
    with self.assertRaises(AssertionError) as error_context:
      self.assertJsonEqual('null', '0', msg='I demand FAILURE')
    self.assertIn('I demand FAILURE', error_context.exception.args[0])
    self.assertIn('None', error_context.exception.args[0])
    with self.assertRaises(AssertionError):
      self.assertJsonEqual('[1, 0, 3]', '[1,2,3]')
    with self.assertRaises(AssertionError):
      self.assertJsonEqual('{"sequence": [1, 2, 3], "float": 23.42}',
                           '{"float": 23.42, "sequence": [1,0,3]}')
    with self.assertRaises(AssertionError):
      self.assertJsonEqual('{"nest": {"spam": "eggs"}, "float": 23.42}',
                           '{"float": 23.42, "nest": {"Spam":"beans"}}')

  def test_assert_json_equal_bad_json(self):
    with self.assertRaises(ValueError) as error_context:
      self.assertJsonEqual("alhg'2;#", '{"a": true}')
    self.assertIn('first', error_context.exception.args[0])
    self.assertIn('alhg', error_context.exception.args[0])

    with self.assertRaises(ValueError) as error_context:
      self.assertJsonEqual('{"a": true}', "alhg'2;#")
    self.assertIn('second', error_context.exception.args[0])
    self.assertIn('alhg', error_context.exception.args[0])

    with self.assertRaises(ValueError) as error_context:
      self.assertJsonEqual('', '')

  @parameterized.named_parameters(
      dict(testcase_name='empty', subset={}, dictionary={}),
      dict(testcase_name='empty_is_a_subset', subset={}, dictionary={'a': 1}),
      dict(
          testcase_name='equal_one_element',
          subset={'a': 1},
          dictionary={'a': 1},
      ),
      dict(
          testcase_name='subset', subset={'a': 1}, dictionary={'a': 1, 'b': 2}
      ),
      dict(
          testcase_name='equal_many_elements',
          subset={'a': 1, 'b': 2},
          dictionary={'a': 1, 'b': 2},
      ),
  )
  def test_assert_dict_contains_subset(
      self, subset: Mapping[Any, Any], dictionary: Mapping[Any, Any]
  ):
    self.assertDictContainsSubset(subset, dictionary)

  def test_assert_dict_contains_subset_converts_to_dict(self):
    class ConvertibleToDict(Mapping):

      def __init__(self, **kwargs):
        self._data = kwargs

      def __getitem__(self, key: Any) -> Any:
        return self._data[key]

      def __iter__(self) -> Iterator:
        return iter(self._data)

      def __len__(self) -> int:
        return len(self._data)

      def keys(self) -> KeysView:
        return self._data.keys()

      def values(self) -> ValuesView:
        return self._data.values()

      def items(self) -> ItemsView:
        return self._data.items()

    self.assertDictContainsSubset(
        ConvertibleToDict(name='a', value=1),
        ConvertibleToDict(name='a', value=1),
    )

  @parameterized.named_parameters(
      dict(testcase_name='subset_vs_empty', subset={1: 'one'}, dictionary={}),
      dict(
          testcase_name='value_is_different',
          subset={'a': 2},
          dictionary={'a': 1},
      ),
      dict(
          testcase_name='key_is_different', subset={'c': 1}, dictionary={'a': 1}
      ),
      dict(
          testcase_name='subset_is_larger',
          subset={'a': 1, 'c': 1},
          dictionary={'a': 1},
      ),
      dict(
          testcase_name='UnicodeDecodeError_constructing_failure_msg',
          subset={'foo': ''.join(chr(i) for i in range(255))},
          dictionary={'foo': '\uFFFD'},
      ),
  )
  def test_assert_dict_contains_subset_fails(
      self, subset: Mapping[Any, Any], dictionary: Mapping[Any, Any]
  ):
    with self.assertRaises(self.failureException):
      self.assertDictContainsSubset(subset, dictionary)

  def test_assert_dict_contains_subset_fails_with_msg(self):
    with self.assertRaisesRegex(
        AssertionError, re.compile('custom message', re.DOTALL)
    ):
      self.assertDictContainsSubset({'a': 1}, {'a': 2}, msg='custom message')


class GetCommandStderrTestCase(absltest.TestCase):

  def test_return_status(self):
    tmpdir = tempfile.mkdtemp(dir=absltest.TEST_TMPDIR.value)
    returncode = (
        absltest.get_command_stderr(
            ['cat', os.path.join(tmpdir, 'file.txt')],
            env=_env_for_command_tests())[0])
    self.assertEqual(1, returncode)

  def test_stderr(self):
    tmpdir = tempfile.mkdtemp(dir=absltest.TEST_TMPDIR.value)
    stderr = (
        absltest.get_command_stderr(
            ['cat', os.path.join(tmpdir, 'file.txt')],
            env=_env_for_command_tests())[1])
    stderr = stderr.decode('utf-8')
    self.assertRegex(stderr, 'No such file or directory')


@contextlib.contextmanager
def cm_for_test(obj):
  try:
    obj.cm_state = 'yielded'
    yield 'value'
  finally:
    obj.cm_state = 'exited'


class EnterContextTest(absltest.TestCase):

  def setUp(self):
    self.cm_state = 'unset'
    self.cm_value = 'unset'

    def assert_cm_exited():
      self.assertEqual(self.cm_state, 'exited')

    # Because cleanup functions are run in reverse order, we have to add
    # our assert-cleanup before the exit stack registers its own cleanup.
    # This ensures we see state after the stack cleanup runs.
    self.addCleanup(assert_cm_exited)

    super().setUp()
    self.cm_value = self.enter_context(cm_for_test(self))

  def test_enter_context(self):
    self.assertEqual(self.cm_value, 'value')
    self.assertEqual(self.cm_state, 'yielded')


class EnterContextClassmethodTest(absltest.TestCase):

  cm_state = 'unset'
  cm_value = 'unset'

  @classmethod
  def setUpClass(cls):

    def assert_cm_exited():
      assert cls.cm_state == 'exited'

    # Because cleanup functions are run in reverse order, we have to add
    # our assert-cleanup before the exit stack registers its own cleanup.
    # This ensures we see state after the stack cleanup runs.
    cls.addClassCleanup(assert_cm_exited)

    super().setUpClass()
    cls.cm_value = cls.enter_context(cm_for_test(cls))

  def test_enter_context(self):
    self.assertEqual(self.cm_value, 'value')
    self.assertEqual(self.cm_state, 'yielded')


class EqualityAssertionTest(absltest.TestCase):
  """This test verifies that absltest.failIfEqual actually tests __ne__.

  If a user class implements __eq__, unittest.assertEqual will call it
  via first == second.   However, failIfEqual also calls
  first == second.   This means that while the caller may believe
  their __ne__ method is being tested, it is not.
  """

  class NeverEqual:
    """Objects of this class behave like NaNs."""

    def __eq__(self, unused_other):
      return False

    def __ne__(self, unused_other):
      return False

  class AllSame:
    """All objects of this class compare as equal."""

    def __eq__(self, unused_other):
      return True

    def __ne__(self, unused_other):
      return False

  class EqualityTestsWithEq:
    """Performs all equality and inequality tests with __eq__."""

    def __init__(self, value):
      self._value = value

    def __eq__(self, other):
      return self._value == other._value

    def __ne__(self, other):
      return not self.__eq__(other)

  class EqualityTestsWithNe:
    """Performs all equality and inequality tests with __ne__."""

    def __init__(self, value):
      self._value = value

    def __eq__(self, other):
      return not self.__ne__(other)

    def __ne__(self, other):
      return self._value != other._value

  class EqualityTestsWithCmp:

    def __init__(self, value):
      self._value = value

    def __cmp__(self, other):
      return cmp(self._value, other._value)

  class EqualityTestsWithLtEq:

    def __init__(self, value):
      self._value = value

    def __eq__(self, other):
      return self._value == other._value

    def __lt__(self, other):
      return self._value < other._value

  def test_all_comparisons_fail(self):
    i1 = self.NeverEqual()
    i2 = self.NeverEqual()
    self.assertFalse(i1 == i2)
    self.assertFalse(i1 != i2)

    # Compare two distinct objects
    self.assertFalse(i1 is i2)
    self.assertRaises(AssertionError, self.assertEqual, i1, i2)
    self.assertRaises(AssertionError, self.assertNotEqual, i1, i2)
    # A NeverEqual object should not compare equal to itself either.
    i2 = i1
    self.assertTrue(i1 is i2)
    self.assertFalse(i1 == i2)
    self.assertFalse(i1 != i2)
    self.assertRaises(AssertionError, self.assertEqual, i1, i2)
    self.assertRaises(AssertionError, self.assertNotEqual, i1, i2)

  def test_all_comparisons_succeed(self):
    a = self.AllSame()
    b = self.AllSame()
    self.assertFalse(a is b)
    self.assertTrue(a == b)
    self.assertFalse(a != b)
    self.assertEqual(a, b)
    self.assertRaises(AssertionError, self.assertNotEqual, a, b)

  def _perform_apple_apple_orange_checks(self, same_a, same_b, different):
    """Perform consistency checks with two apples and an orange.

    The two apples should always compare as being the same (and inequality
    checks should fail).  The orange should always compare as being different
    to each of the apples.

    Args:
      same_a: the first apple
      same_b: the second apple
      different: the orange
    """
    self.assertTrue(same_a == same_b)
    self.assertFalse(same_a != same_b)
    self.assertEqual(same_a, same_b)

    self.assertFalse(same_a == different)
    self.assertTrue(same_a != different)
    self.assertNotEqual(same_a, different)

    self.assertFalse(same_b == different)
    self.assertTrue(same_b != different)
    self.assertNotEqual(same_b, different)

  def test_comparison_with_eq(self):
    same_a = self.EqualityTestsWithEq(42)
    same_b = self.EqualityTestsWithEq(42)
    different = self.EqualityTestsWithEq(1769)
    self._perform_apple_apple_orange_checks(same_a, same_b, different)

  def test_comparison_with_ne(self):
    same_a = self.EqualityTestsWithNe(42)
    same_b = self.EqualityTestsWithNe(42)
    different = self.EqualityTestsWithNe(1769)
    self._perform_apple_apple_orange_checks(same_a, same_b, different)

  def test_comparison_with_cmp_or_lt_eq(self):
    same_a = self.EqualityTestsWithLtEq(42)
    same_b = self.EqualityTestsWithLtEq(42)
    different = self.EqualityTestsWithLtEq(1769)
    self._perform_apple_apple_orange_checks(same_a, same_b, different)


class AssertSequenceStartsWithTest(parameterized.TestCase):

  def setUp(self):
    super().setUp()
    self.a = [5, 'foo', {'c': 'd'}, None]

  def test_empty_sequence_starts_with_empty_prefix(self):
    self.assertSequenceStartsWith([], ())

  def test_sequence_prefix_is_an_empty_list(self):
    self.assertSequenceStartsWith([[]], ([], 'foo'))

  def test_raise_if_empty_prefix_with_non_empty_whole(self):
    with self.assertRaisesRegex(
        AssertionError, 'Prefix length is 0 but whole length is %d: %s' % (len(
            self.a), r"\[5, 'foo', \{'c': 'd'\}, None\]")):
      self.assertSequenceStartsWith([], self.a)

  def test_single_element_prefix(self):
    self.assertSequenceStartsWith([5], self.a)

  def test_two_element_prefix(self):
    self.assertSequenceStartsWith((5, 'foo'), self.a)

  def test_prefix_is_full_sequence(self):
    self.assertSequenceStartsWith([5, 'foo', {'c': 'd'}, None], self.a)

  def test_string_prefix(self):
    self.assertSequenceStartsWith('abc', 'abc123')

  def test_convert_non_sequence_prefix_to_sequence_and_try_again(self):
    self.assertSequenceStartsWith(5, self.a)

  def test_whole_not_asequence(self):
    msg = (r'For whole: len\(5\) is not supported, it appears to be type: '
           '<(type|class) \'int\'>')
    with self.assertRaisesRegex(AssertionError, msg):
      self.assertSequenceStartsWith(self.a, 5)

  def test_raise_if_sequence_does_not_start_with_prefix(self):
    msg = (r"prefix: \['foo', \{'c': 'd'\}\] not found at start of whole: "
           r"\[5, 'foo', \{'c': 'd'\}, None\].")
    with self.assertRaisesRegex(AssertionError, msg):
      self.assertSequenceStartsWith(['foo', {'c': 'd'}], self.a)

  @parameterized.named_parameters(
      ('dict', {'a': 1, 2: 'b'}, {'a': 1, 2: 'b', 'c': '3'}),
      ('set', {1, 2}, {1, 2, 3}),
  )
  def test_raise_if_set_or_dict(self, prefix, whole):
    with self.assertRaisesRegex(
        AssertionError, 'For whole: Mapping or Set objects are not supported'
    ):
      self.assertSequenceStartsWith(prefix, whole)


class TestAssertEmpty(absltest.TestCase):
  longMessage = True

  def test_raises_if_not_asized_object(self):
    msg = "Expected a Sized object, got: 'int'"
    with self.assertRaisesRegex(AssertionError, msg):
      self.assertEmpty(1)

  def test_calls_len_not_bool(self):

    class BadList(list):

      def __bool__(self):
        return False

      __nonzero__ = __bool__

    bad_list = BadList()
    self.assertEmpty(bad_list)
    self.assertFalse(bad_list)

  def test_passes_when_empty(self):
    empty_containers = [
        list(),
        tuple(),
        dict(),
        set(),
        frozenset(),
        b'',
        '',
        bytearray(),
    ]
    for container in empty_containers:
      self.assertEmpty(container)

  def test_raises_with_not_empty_containers(self):
    not_empty_containers = [
        [1],
        (1,),
        {'foo': 'bar'},
        {1},
        frozenset([1]),
        b'a',
        'a',
        bytearray(b'a'),
    ]
    regexp = r'.* has length of 1\.$'
    for container in not_empty_containers:
      with self.assertRaisesRegex(AssertionError, regexp):
        self.assertEmpty(container)

  def test_user_message_added_to_default(self):
    msg = 'This is a useful message'
    whole_msg = re.escape('[1] has length of 1. : This is a useful message')
    with self.assertRaisesRegex(AssertionError, whole_msg):
      self.assertEmpty([1], msg=msg)


class TestAssertNotEmpty(absltest.TestCase):
  longMessage = True

  def test_raises_if_not_asized_object(self):
    msg = "Expected a Sized object, got: 'int'"
    with self.assertRaisesRegex(AssertionError, msg):
      self.assertNotEmpty(1)

  def test_calls_len_not_bool(self):

    class BadList(list):

      def __bool__(self):
        return False

      __nonzero__ = __bool__

    bad_list = BadList([1])
    self.assertNotEmpty(bad_list)
    self.assertFalse(bad_list)

  def test_passes_when_not_empty(self):
    not_empty_containers = [
        [1],
        (1,),
        {'foo': 'bar'},
        {1},
        frozenset([1]),
        b'a',
        'a',
        bytearray(b'a'),
    ]
    for container in not_empty_containers:
      self.assertNotEmpty(container)

  def test_raises_with_empty_containers(self):
    empty_containers = [
        list(),
        tuple(),
        dict(),
        set(),
        frozenset(),
        b'',
        '',
        bytearray(),
    ]
    regexp = r'.* has length of 0\.$'
    for container in empty_containers:
      with self.assertRaisesRegex(AssertionError, regexp):
        self.assertNotEmpty(container)

  def test_user_message_added_to_default(self):
    msg = 'This is a useful message'
    whole_msg = re.escape('[] has length of 0. : This is a useful message')
    with self.assertRaisesRegex(AssertionError, whole_msg):
      self.assertNotEmpty([], msg=msg)


class TestAssertLen(absltest.TestCase):
  longMessage = True

  def test_raises_if_not_asized_object(self):
    msg = "Expected a Sized object, got: 'int'"
    with self.assertRaisesRegex(AssertionError, msg):
      self.assertLen(1, 1)

  def test_passes_when_expected_len(self):
    containers = [
        [[1], 1],
        [(1, 2), 2],
        [{'a': 1, 'b': 2, 'c': 3}, 3],
        [{1, 2, 3, 4}, 4],
        [frozenset([1]), 1],
        [b'abc', 3],
        ['def', 3],
        [bytearray(b'ghij'), 4],
    ]
    for container, expected_len in containers:
      self.assertLen(container, expected_len)

  def test_raises_when_unexpected_len(self):
    containers = [
        [1],
        (1, 2),
        {'a': 1, 'b': 2, 'c': 3},
        {1, 2, 3, 4},
        frozenset([1]),
        b'abc',
        'def',
        bytearray(b'ghij'),
    ]
    for container in containers:
      regexp = r'.* has length of %d, expected 100\.$' % len(container)
      with self.assertRaisesRegex(AssertionError, regexp):
        self.assertLen(container, 100)

  def test_user_message_added_to_default(self):
    msg = 'This is a useful message'
    whole_msg = (
        r'\[1\] has length of 1, expected 100. : This is a useful message')
    with self.assertRaisesRegex(AssertionError, whole_msg):
      self.assertLen([1], 100, msg)


class TestLoaderTest(absltest.TestCase):
  """Tests that the TestLoader bans methods named TestFoo."""

  # pylint: disable=invalid-name
  class Valid(absltest.TestCase):
    """Test case containing a variety of valid names."""

    test_property = 1
    TestProperty = 2

    @staticmethod
    def TestStaticMethod():
      pass

    @staticmethod
    def TestStaticMethodWithArg(foo):
      pass

    @classmethod
    def TestClassMethod(cls):
      pass

    def Test(self):
      pass

    def TestingHelper(self):
      pass

    def testMethod(self):
      pass

    def TestHelperWithParams(self, a, b):
      pass

    def TestHelperWithVarargs(self, *args, **kwargs):
      pass

    def TestHelperWithDefaults(self, a=5):
      pass

    def TestHelperWithKeywordOnly(self, *, arg):
      pass

  class Invalid(absltest.TestCase):
    """Test case containing a suspicious method."""

    def testMethod(self):
      pass

    def TestSuspiciousMethod(self):
      pass
  # pylint: enable=invalid-name

  def setUp(self):
    self.loader = absltest.TestLoader()

  def test_valid(self):
    suite = self.loader.loadTestsFromTestCase(TestLoaderTest.Valid)
    self.assertEqual(1, suite.countTestCases())

  def testInvalid(self):
    with self.assertRaisesRegex(TypeError, 'TestSuspiciousMethod'):
      self.loader.loadTestsFromTestCase(TestLoaderTest.Invalid)


class InitNotNecessaryForAssertsTest(absltest.TestCase):
  """TestCase assertions should work even if __init__ wasn't correctly called.

  This is a workaround, see comment in
  absltest.TestCase._getAssertEqualityFunc. We know that not calling
  __init__ of a superclass is a bad thing, but people keep doing them,
  and this (even if a little bit dirty) saves them from shooting
  themselves in the foot.
  """

  def test_subclass(self):

    class Subclass(absltest.TestCase):

      def __init__(self):  # pylint: disable=super-init-not-called
        pass

    Subclass().assertEqual({}, {})

  def test_multiple_inheritance(self):

    class Foo:

      def __init__(self, *args, **kwargs):
        pass

    class Subclass(Foo, absltest.TestCase):
      pass

    Subclass().assertEqual({}, {})


@dataclasses.dataclass
class _ExampleDataclass:
  comparable: str
  not_comparable: str = dataclasses.field(compare=False)
  comparable2: str = 'comparable2'


@dataclasses.dataclass
class _ExampleCustomEqualDataclass:
  value: str

  def __eq__(self, other):
    return False


class TestAssertDataclassEqual(absltest.TestCase):

  def test_assert_dataclass_equal_checks_a_for_dataclass(self):
    b = _ExampleDataclass('a', 'b')

    message = 'First argument is not a dataclass instance.'
    with self.assertRaisesWithLiteralMatch(AssertionError, message):
      self.assertDataclassEqual('a', b)

  def test_assert_dataclass_equal_checks_b_for_dataclass(self):
    a = _ExampleDataclass('a', 'b')

    message = 'Second argument is not a dataclass instance.'
    with self.assertRaisesWithLiteralMatch(AssertionError, message):
      self.assertDataclassEqual(a, 'b')

  def test_assert_dataclass_equal_different_dataclasses(self):
    a = _ExampleDataclass('a', 'b')
    b = _ExampleCustomEqualDataclass('c')

    message = """Found different dataclass types: <class '__main__._ExampleDataclass'> != <class '__main__._ExampleCustomEqualDataclass'>"""
    with self.assertRaisesWithLiteralMatch(AssertionError, message):
      self.assertDataclassEqual(a, b)

  def test_assert_dataclass_equal(self):
    a = _ExampleDataclass(comparable='a', not_comparable='b')
    b = _ExampleDataclass(comparable='a', not_comparable='c')

    self.assertDataclassEqual(a, a)
    self.assertDataclassEqual(a, b)
    self.assertDataclassEqual(b, a)

  def test_assert_dataclass_fails_non_equal_classes_assert_dict_passes(self):
    a = _ExampleCustomEqualDataclass(value='a')
    b = _ExampleCustomEqualDataclass(value='a')

    message = textwrap.dedent("""\
        _ExampleCustomEqualDataclass(value='a') != _ExampleCustomEqualDataclass(value='a')
        Cannot detect difference by examining the fields of the dataclass.""")
    with self.assertRaisesWithLiteralMatch(AssertionError, message):
      self.assertDataclassEqual(a, b)

  def test_assert_dataclass_fails_assert_dict_fails_one_field(self):
    a = _ExampleDataclass(comparable='a', not_comparable='b')
    b = _ExampleDataclass(comparable='c', not_comparable='d')

    message = textwrap.dedent("""\
        _ExampleDataclass(comparable='a', not_comparable='b', comparable2='comparable2') != _ExampleDataclass(comparable='c', not_comparable='d', comparable2='comparable2')
        Fields that differ:
        comparable: 'a' != 'c'""")
    with self.assertRaisesWithLiteralMatch(AssertionError, message):
      self.assertDataclassEqual(a, b)

  def test_assert_dataclass_fails_assert_dict_fails_multiple_fields(self):
    a = _ExampleDataclass(comparable='a', not_comparable='b', comparable2='c')
    b = _ExampleDataclass(comparable='c', not_comparable='d', comparable2='e')

    message = textwrap.dedent("""\
        _ExampleDataclass(comparable='a', not_comparable='b', comparable2='c') != _ExampleDataclass(comparable='c', not_comparable='d', comparable2='e')
        Fields that differ:
        comparable: 'a' != 'c'
        comparable2: 'c' != 'e'""")
    with self.assertRaisesWithLiteralMatch(AssertionError, message):
      self.assertDataclassEqual(a, b)


class GetCommandStringTest(parameterized.TestCase):

  @parameterized.parameters(
      ([], '', ''),
      ([''], "''", ''),
      (['command', 'arg-0'], "'command' 'arg-0'", 'command arg-0'),
      (['command', 'arg-0'], "'command' 'arg-0'", 'command arg-0'),
      (["foo'bar"], "'foo'\"'\"'bar'", "foo'bar"),
      (['foo"bar'], "'foo\"bar'", 'foo"bar'),
      ('command arg-0', 'command arg-0', 'command arg-0'),
      ('command arg-0', 'command arg-0', 'command arg-0'),
  )
  def test_get_command_string(
      self, command, expected_non_windows, expected_windows):
    expected = expected_windows if os.name == 'nt' else expected_non_windows
    self.assertEqual(expected, absltest.get_command_string(command))


class TempFileTest(BaseTestCase):

  def assert_dir_exists(self, temp_dir):
    path = temp_dir.full_path
    self.assertTrue(os.path.exists(path), f'Dir {path} does not exist')
    self.assertTrue(
        os.path.isdir(path), f'Path {path} exists, but is not a directory'
    )

  def assert_file_exists(self, temp_file, expected_content=b''):
    path = temp_file.full_path
    self.assertTrue(os.path.exists(path), f'File {path} does not exist')
    self.assertTrue(
        os.path.isfile(path), f'Path {path} exists, but is not a file'
    )

    mode = 'rb' if isinstance(expected_content, bytes) else 'rt'
    with open(path, mode) as fp:
      actual = fp.read()
    self.assertEqual(expected_content, actual)

  def run_tempfile_helper(self, cleanup, expected_paths):
    tmpdir = self.create_tempdir('helper-test-temp-dir')
    env = {
        'ABSLTEST_TEST_HELPER_TEMPFILE_CLEANUP': cleanup,
        'TEST_TMPDIR': tmpdir.full_path,
        }
    stdout, stderr, _ = self.run_helper(
        0, ['TempFileHelperTest'], env, expect_success=False
    )
    output = ('\n=== Helper output ===\n'
              '----- stdout -----\n{}\n'
              '----- end stdout -----\n'
              '----- stderr -----\n{}\n'
              '----- end stderr -----\n'
              '===== end helper output =====').format(stdout, stderr)
    self.assertIn('test_failure', stderr, output)

    # Adjust paths to match on Windows
    expected_paths = {path.replace('/', os.sep) for path in expected_paths}

    actual = {
        os.path.relpath(f, tmpdir.full_path)
        for f in _listdir_recursive(tmpdir.full_path)
        if f != tmpdir.full_path
    }
    self.assertEqual(expected_paths, actual, output)

  def test_create_file_pre_existing_readonly(self):
    first = self.create_tempfile('foo', content='first')
    os.chmod(first.full_path, 0o444)
    second = self.create_tempfile('foo', content='second')
    self.assertEqual('second', first.read_text())
    self.assertEqual('second', second.read_text())

  def test_create_file_fails_cleanup(self):
    path = self.create_tempfile().full_path
    # Removing the write bit from the file makes it undeletable on Windows.
    os.chmod(path, 0)
    # Removing the write bit from the whole directory makes all contained files
    # undeletable on unix. We also need it to be exec so that os.path.isfile
    # returns true, and we reach the buggy branch.
    os.chmod(os.path.dirname(path), stat.S_IEXEC)
    # The test should pass, even though that file cannot be deleted in teardown.

  def test_temp_file_path_like(self):
    tempdir = self.create_tempdir('foo')
    tempfile_ = tempdir.create_file('bar')

    self.assertEqual(tempfile_.read_text(), pathlib.Path(tempfile_).read_text())
    # assertIsInstance causes the types to be narrowed, so calling create_file
    # and read_text() must be done before these assertions to avoid type errors.
    self.assertIsInstance(tempdir, os.PathLike)
    self.assertIsInstance(tempfile_, os.PathLike)

  def test_unnamed(self):
    td = self.create_tempdir()
    self.assert_dir_exists(td)

    tdf = td.create_file()
    self.assert_file_exists(tdf)

    tdd = td.mkdir()
    self.assert_dir_exists(tdd)

    tf = self.create_tempfile()
    self.assert_file_exists(tf)

  def test_named(self):
    td = self.create_tempdir('d')
    self.assert_dir_exists(td)

    tdf = td.create_file('df')
    self.assert_file_exists(tdf)

    tdd = td.mkdir('dd')
    self.assert_dir_exists(tdd)

    tf = self.create_tempfile('f')
    self.assert_file_exists(tf)

  def test_nested_paths(self):
    td = self.create_tempdir('d1/d2')
    self.assert_dir_exists(td)

    tdf = td.create_file('df1/df2')
    self.assert_file_exists(tdf)

    tdd = td.mkdir('dd1/dd2')
    self.assert_dir_exists(tdd)

    tf = self.create_tempfile('f1/f2')
    self.assert_file_exists(tf)

  def test_tempdir_create_file(self):
    td = self.create_tempdir()
    td.create_file(content='text')

  def test_tempfile_text(self):
    tf = self.create_tempfile(content='text')
    self.assert_file_exists(tf, 'text')
    self.assertEqual('text', tf.read_text())

    with tf.open_text() as fp:
      self.assertEqual('text', fp.read())

    with tf.open_text('w') as fp:
      fp.write('text-from-open-write')
    self.assertEqual('text-from-open-write', tf.read_text())

    tf.write_text('text-from-write-text')
    self.assertEqual('text-from-write-text', tf.read_text())

  def test_tempfile_bytes(self):
    tf = self.create_tempfile(content=b'\x00\x01\x02')
    self.assert_file_exists(tf, b'\x00\x01\x02')
    self.assertEqual(b'\x00\x01\x02', tf.read_bytes())

    with tf.open_bytes() as fp:
      self.assertEqual(b'\x00\x01\x02', fp.read())

    with tf.open_bytes('wb') as fp:
      fp.write(b'\x03')
    self.assertEqual(b'\x03', tf.read_bytes())

    tf.write_bytes(b'\x04')
    self.assertEqual(b'\x04', tf.read_bytes())

  def test_tempdir_same_name(self):
    """Make sure the same directory name can be used."""
    td1 = self.create_tempdir('foo')
    td2 = self.create_tempdir('foo')
    self.assert_dir_exists(td1)
    self.assert_dir_exists(td2)

  def test_tempfile_cleanup_success(self):
    expected = {
        'TempFileHelperTest',
        'TempFileHelperTest/test_failure',
        'TempFileHelperTest/test_failure/failure',
        'TempFileHelperTest/test_success',
        'TempFileHelperTest/test_subtest_failure',
        'TempFileHelperTest/test_subtest_failure/parent',
        'TempFileHelperTest/test_subtest_failure/successful_child',
        'TempFileHelperTest/test_subtest_failure/failed_child',
        'TempFileHelperTest/test_subtest_success',
    }
    self.run_tempfile_helper('SUCCESS', expected)

  def test_tempfile_cleanup_always(self):
    expected = {
        'TempFileHelperTest',
        'TempFileHelperTest/test_failure',
        'TempFileHelperTest/test_success',
        'TempFileHelperTest/test_subtest_failure',
        'TempFileHelperTest/test_subtest_success',
    }
    self.run_tempfile_helper('ALWAYS', expected)

  def test_tempfile_cleanup_off(self):
    expected = {
        'TempFileHelperTest',
        'TempFileHelperTest/test_failure',
        'TempFileHelperTest/test_failure/failure',
        'TempFileHelperTest/test_success',
        'TempFileHelperTest/test_success/success',
        'TempFileHelperTest/test_subtest_failure',
        'TempFileHelperTest/test_subtest_failure/parent',
        'TempFileHelperTest/test_subtest_failure/successful_child',
        'TempFileHelperTest/test_subtest_failure/failed_child',
        'TempFileHelperTest/test_subtest_success',
        'TempFileHelperTest/test_subtest_success/parent',
        'TempFileHelperTest/test_subtest_success/child0',
        'TempFileHelperTest/test_subtest_success/child1',
    }
    self.run_tempfile_helper('OFF', expected)


class SkipClassTest(absltest.TestCase):

  def test_incorrect_decorator_call(self):
    with self.assertRaises(TypeError):

      # Disabling type checking because pytype correctly picks up that
      # @absltest.skipThisClass is being used incorrectly.
      # pytype: disable=wrong-arg-types
      @absltest.skipThisClass
      class Test(absltest.TestCase):  # pylint: disable=unused-variable
        pass
      # pytype: enable=wrong-arg-types

  def test_incorrect_decorator_subclass(self):
    with self.assertRaises(TypeError):

      @absltest.skipThisClass('reason')
      def test_method():  # pylint: disable=unused-variable
        pass

  def test_correct_decorator_class(self):

    @absltest.skipThisClass('reason')
    class Test(absltest.TestCase):
      pass

    with self.assertRaises(absltest.SkipTest):
      Test.setUpClass()

  def test_correct_decorator_subclass(self):

    @absltest.skipThisClass('reason')
    class Test(absltest.TestCase):
      pass

    class Subclass(Test):
      pass

    with self.subTest('Base class should be skipped'):
      with self.assertRaises(absltest.SkipTest):
        Test.setUpClass()

    with self.subTest('Subclass should not be skipped'):
      Subclass.setUpClass()  # should not raise.

  def test_setup(self):

    @absltest.skipThisClass('reason')
    class Test(absltest.TestCase):

      @classmethod
      def setUpClass(cls):
        super().setUpClass()
        cls.foo = 1

    class Subclass(Test):
      pass

    Subclass.setUpClass()
    self.assertEqual(Subclass.foo, 1)

  def test_setup_chain(self) -> None:

    @absltest.skipThisClass('reason')
    class BaseTest(absltest.TestCase):

      foo: int

      @classmethod
      def setUpClass(cls):
        super().setUpClass()
        cls.foo = 1

    @absltest.skipThisClass('reason')
    class SecondBaseTest(BaseTest):

      bar: int

      @classmethod
      def setUpClass(cls):
        super().setUpClass()
        cls.bar = 2

    class Subclass(SecondBaseTest):
      pass

    Subclass.setUpClass()
    self.assertEqual(Subclass.foo, 1)
    self.assertEqual(Subclass.bar, 2)

  def test_setup_args(self) -> None:

    @absltest.skipThisClass('reason')
    class Test(absltest.TestCase):
      foo: str
      bar: Optional[str]

      @classmethod
      def setUpClass(cls, foo, bar=None):
        super().setUpClass()
        cls.foo = foo
        cls.bar = bar

    class Subclass(Test):

      @classmethod
      def setUpClass(cls):
        super().setUpClass('foo', bar='baz')

    Subclass.setUpClass()
    self.assertEqual(Subclass.foo, 'foo')
    self.assertEqual(Subclass.bar, 'baz')

  def test_setup_multiple_inheritance(self) -> None:

    # Test that skipping this class doesn't break the MRO chain and stop
    # RequiredBase.setUpClass from running.
    @absltest.skipThisClass('reason')
    class Left(absltest.TestCase):
      pass

    class RequiredBase(absltest.TestCase):
      foo: str

      @classmethod
      def setUpClass(cls):
        super().setUpClass()
        cls.foo = 'foo'

    class Right(RequiredBase):

      @classmethod
      def setUpClass(cls):
        super().setUpClass()

    # Test will fail unless Left.setUpClass() follows mro properly
    # Right.setUpClass()
    class Subclass(Left, Right):

      @classmethod
      def setUpClass(cls):
        super().setUpClass()

    class Test(Subclass):
      pass

    Test.setUpClass()
    self.assertEqual(Test.foo, 'foo')

  def test_skip_class(self):

    @absltest.skipThisClass('reason')
    class BaseTest(absltest.TestCase):

      def test_foo(self):
        _ = 1 / 0

    class Test(BaseTest):

      def test_foo(self):
        self.assertEqual(1, 1)

    with self.subTest('base class'):
      ts = unittest.defaultTestLoader.loadTestsFromTestCase(BaseTest)
      self.assertEqual(1, ts.countTestCases())

      res = unittest.TestResult()
      ts.run(res)
      self.assertTrue(res.wasSuccessful())
      self.assertLen(res.skipped, 1)
      self.assertEqual(0, res.testsRun)
      self.assertEmpty(res.failures)
      self.assertEmpty(res.errors)

    with self.subTest('real test'):
      ts = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
      self.assertEqual(1, ts.countTestCases())

      res = unittest.TestResult()
      ts.run(res)
      self.assertTrue(res.wasSuccessful())
      self.assertEqual(1, res.testsRun)
      self.assertEmpty(res.skipped)
      self.assertEmpty(res.failures)
      self.assertEmpty(res.errors)

  def test_skip_class_unittest(self):

    @absltest.skipThisClass('reason')
    class Test(unittest.TestCase):  # note: unittest not absltest

      def test_foo(self):
        _ = 1 / 0

    ts = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
    self.assertEqual(1, ts.countTestCases())

    res = unittest.TestResult()
    ts.run(res)
    self.assertTrue(res.wasSuccessful())
    self.assertLen(res.skipped, 1)
    self.assertEqual(0, res.testsRun)
    self.assertEmpty(res.failures)
    self.assertEmpty(res.errors)


class ExitCodeTest(BaseTestCase):

  def test_exits_5_when_no_tests(self):
    expect_success = sys.version_info < (3, 12)
    _, _, exit_code = self.run_helper(
        None,
        [],
        {},
        expect_success=expect_success,
        helper_name='absltest_test_helper_skipped',
    )
    if not expect_success:
      self.assertEqual(exit_code, 5)

  def test_exits_5_when_all_skipped(self):
    self.run_helper(
        None,
        [],
        {'ABSLTEST_TEST_HELPER_DEFINE_CLASS': '1'},
        expect_success=True,
        helper_name='absltest_test_helper_skipped',
    )


def _listdir_recursive(path):
  for dirname, _, filenames in os.walk(path):
    yield dirname
    for filename in filenames:
      yield os.path.join(dirname, filename)


def _env_for_command_tests():
  if os.name == 'nt' and 'PATH' in os.environ:
    # get_command_stderr and assertCommandXXX don't inherit environment
    # variables by default. This makes sure msys commands can be found on
    # Windows.
    return {'PATH': os.environ['PATH']}
  else:
    return None


if __name__ == '__main__':
  absltest.main()
