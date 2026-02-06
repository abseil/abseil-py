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
"""Tests for flagsaver."""

from absl import flags
from absl.testing import absltest
from absl.testing import flagsaver
from absl.testing import parameterized

flags.DEFINE_string('flagsaver_test_flag0', 'unchanged0', 'flag to test with')
flags.DEFINE_string('flagsaver_test_flag1', 'unchanged1', 'flag to test with')

flags.DEFINE_string('flagsaver_test_validated_flag', None, 'flag to test with')
flags.register_validator('flagsaver_test_validated_flag', lambda x: not x)

flags.DEFINE_string('flagsaver_test_validated_flag1', None, 'flag to test with')
flags.DEFINE_string('flagsaver_test_validated_flag2', None, 'flag to test with')

INT_FLAG = flags.DEFINE_integer(
    'flagsaver_test_int_flag', default=1, help='help')
STR_FLAG = flags.DEFINE_string(
    'flagsaver_test_str_flag', default='str default', help='help')

MULTI_INT_FLAG = flags.DEFINE_multi_integer('flagsaver_test_multi_int_flag',
                                            None, 'flag to test with')


@flags.multi_flags_validator(
    ('flagsaver_test_validated_flag1', 'flagsaver_test_validated_flag2'))
def validate_test_flags(flag_dict):
  return (flag_dict['flagsaver_test_validated_flag1'] ==
          flag_dict['flagsaver_test_validated_flag2'])


FLAGS = flags.FLAGS


@flags.validator('flagsaver_test_flag0')
def check_no_upper_case(value):
  return value == value.lower()


class _TestError(Exception):
  """Exception class for use in these tests."""


class CommonUsageTest(absltest.TestCase):
  """These test cases cover the most common usages of flagsaver."""

  def test_as_parsed_context_manager(self):
    # Precondition check, we expect all the flags to start as their default.
    self.assertEqual('str default', STR_FLAG.value)
    self.assertFalse(STR_FLAG.present)
    self.assertEqual(1, INT_FLAG.value)
    self.assertEqual('unchanged0', FLAGS.flagsaver_test_flag0)
    self.assertEqual('unchanged1', FLAGS.flagsaver_test_flag1)

    # Flagsaver will also save the state of flags that have been modified.
    FLAGS.flagsaver_test_flag1 = 'outside flagsaver'

    # Save all existing flag state, and set some flags as if they were parsed on
    # the command line. Because of this, the new values must be provided as str,
    # even if the flag type is something other than string.
    with flagsaver.as_parsed(
        (STR_FLAG, 'new string value'),  # Override using flagholder object.
        (INT_FLAG, '123'),  # Override an int flag (NOTE: must specify as str).
        flagsaver_test_flag0='new value',  # Override using flag name.
    ):
      # All the flags have their overridden values.
      self.assertEqual('new string value', STR_FLAG.value)
      self.assertTrue(STR_FLAG.present)
      self.assertEqual(123, INT_FLAG.value)
      self.assertEqual('new value', FLAGS.flagsaver_test_flag0)
      # Even if we change other flags, they will reset on context exit.
      FLAGS.flagsaver_test_flag1 = 'new value 1'

    # The flags have all reset to their pre-flagsaver values.
    self.assertEqual('str default', STR_FLAG.value)
    self.assertFalse(STR_FLAG.present)
    self.assertEqual(1, INT_FLAG.value)
    self.assertEqual('unchanged0', FLAGS.flagsaver_test_flag0)
    self.assertEqual('outside flagsaver', FLAGS.flagsaver_test_flag1)

  def test_as_parsed_decorator(self):
    # flagsaver.as_parsed can also be used as a decorator.
    @flagsaver.as_parsed((INT_FLAG, '123'))
    def do_something_with_flags():
      self.assertEqual(123, INT_FLAG.value)
      self.assertTrue(INT_FLAG.present)

    do_something_with_flags()
    self.assertEqual(1, INT_FLAG.value)
    self.assertFalse(INT_FLAG.present)

  def test_flagsaver_flagsaver(self):
    # If you don't want the flags to go through parsing, you can instead use
    # flagsaver.flagsaver(). With this method, you provide the native python
    # value you'd like the flags to take on. Otherwise it functions similar to
    # flagsaver.as_parsed().
    @flagsaver.flagsaver((INT_FLAG, 345))
    def do_something_with_flags():
      self.assertEqual(345, INT_FLAG.value)
      # Note that because this flag was never parsed, it will not register as
      # .present unless you manually set that attribute.
      self.assertFalse(INT_FLAG.present)
      # If you do chose to modify things about the flag (such as .present) those
      # changes will still be cleaned up when flagsaver.flagsaver() exits.
      INT_FLAG.present = True

    self.assertEqual(1, INT_FLAG.value)
    # flagsaver.flagsaver() restored INT_FLAG.present to the state it was in
    # before entering the context.
    self.assertFalse(INT_FLAG.present)


class SaveFlagValuesTest(absltest.TestCase):
  """Test flagsaver.save_flag_values() and flagsaver.restore_flag_values().

  In this test, we insure that *all* properties of flags get restored. In other
  tests we only try changing the flag value.
  """

  def test_assign_value(self):
    # First save the flag values.
    saved_flag_values = flagsaver.save_flag_values()

    # Now mutate the flag's value field and check that it changed.
    FLAGS.flagsaver_test_flag0 = 'new value'
    self.assertEqual('new value', FLAGS.flagsaver_test_flag0)

    # Now restore the flag to its original value.
    flagsaver.restore_flag_values(saved_flag_values)
    self.assertEqual('unchanged0', FLAGS.flagsaver_test_flag0)

  def test_set_default(self):
    # First save the flag.
    saved_flag_values = flagsaver.save_flag_values()

    # Now mutate the flag's default field and check that it changed.
    FLAGS.set_default('flagsaver_test_flag0', 'new_default')
    self.assertEqual('new_default', FLAGS['flagsaver_test_flag0'].default)

    # Now restore the flag's default field.
    flagsaver.restore_flag_values(saved_flag_values)
    self.assertEqual('unchanged0', FLAGS['flagsaver_test_flag0'].default)

  def test_parse(self):
    # First save the flag.
    saved_flag_values = flagsaver.save_flag_values()

    # Sanity check (would fail if called with --flagsaver_test_flag0).
    self.assertEqual(0, FLAGS['flagsaver_test_flag0'].present)
    # Now populate the flag and check that it changed.
    FLAGS['flagsaver_test_flag0'].parse('new value')
    self.assertEqual('new value', FLAGS['flagsaver_test_flag0'].value)
    self.assertEqual(1, FLAGS['flagsaver_test_flag0'].present)

    # Now restore the flag to its original value.
    flagsaver.restore_flag_values(saved_flag_values)
    self.assertEqual('unchanged0', FLAGS['flagsaver_test_flag0'].value)
    self.assertEqual(0, FLAGS['flagsaver_test_flag0'].present)

  def test_assign_validators(self):
    # First save the flag.
    saved_flag_values = flagsaver.save_flag_values()

    # Sanity check that a validator already exists.
    self.assertLen(FLAGS['flagsaver_test_flag0'].validators, 1)
    original_validators = list(FLAGS['flagsaver_test_flag0'].validators)

    def no_space(value):
      return ' ' not in value

    # Add a new validator.
    flags.register_validator('flagsaver_test_flag0', no_space)
    self.assertLen(FLAGS['flagsaver_test_flag0'].validators, 2)

    # Now restore the flag to its original value.
    flagsaver.restore_flag_values(saved_flag_values)
    self.assertEqual(
        original_validators, FLAGS['flagsaver_test_flag0'].validators
    )


@parameterized.named_parameters(
    dict(
        testcase_name='flagsaver.flagsaver',
        flagsaver_method=flagsaver.flagsaver,
    ),
    dict(
        testcase_name='flagsaver.as_parsed',
        flagsaver_method=flagsaver.as_parsed,
    ),
)
class NoOverridesTest(parameterized.TestCase):
  """Test flagsaver.flagsaver and flagsaver.as_parsed without overrides."""

  def test_context_manager_with_call(self, flagsaver_method):
    with flagsaver_method():
      FLAGS.flagsaver_test_flag0 = 'new value'
    self.assertEqual('unchanged0', FLAGS.flagsaver_test_flag0)

  def test_context_manager_with_exception(self, flagsaver_method):
    with self.assertRaises(_TestError):
      with flagsaver_method():
        FLAGS.flagsaver_test_flag0 = 'new value'
        # Simulate a failed test.
        raise _TestError('something happened')
    self.assertEqual('unchanged0', FLAGS.flagsaver_test_flag0)

  def test_decorator_without_call(self, flagsaver_method):
    @flagsaver_method
    def mutate_flags():
      FLAGS.flagsaver_test_flag0 = 'new value'

    mutate_flags()
    self.assertEqual('unchanged0', FLAGS.flagsaver_test_flag0)

  def test_decorator_with_call(self, flagsaver_method):
    @flagsaver_method()
    def mutate_flags():
      FLAGS.flagsaver_test_flag0 = 'new value'

    mutate_flags()
    self.assertEqual('unchanged0', FLAGS.flagsaver_test_flag0)

  def test_decorator_with_exception(self, flagsaver_method):
    @flagsaver_method()
    def raise_exception():
      FLAGS.flagsaver_test_flag0 = 'new value'
      # Simulate a failed test.
      raise _TestError('something happened')

    self.assertEqual('unchanged0', FLAGS.flagsaver_test_flag0)
    self.assertRaises(_TestError, raise_exception)
    self.assertEqual('unchanged0', FLAGS.flagsaver_test_flag0)


@parameterized.named_parameters(
    dict(
        testcase_name='flagsaver.flagsaver',
        flagsaver_method=flagsaver.flagsaver,
    ),
    dict(
        testcase_name='flagsaver.as_parsed',
        flagsaver_method=flagsaver.as_parsed,
    ),
)
class TestStringFlagOverrides(parameterized.TestCase):
  """Test flagsaver.flagsaver and flagsaver.as_parsed with string overrides.

  Note that these tests can be parameterized because both .flagsaver and
  .as_parsed expect a str input when overriding a string flag. For non-string
  flags these two flagsaver methods have separate tests elsewhere in this file.

  Each test is one class of overrides, executed twice. Once as a context
  manager, and once as a decorator on a mutate_flags() method.
  """

  def test_keyword_overrides(self, flagsaver_method):
    # Context manager:
    with flagsaver_method(flagsaver_test_flag0='new value'):
      self.assertEqual('new value', FLAGS.flagsaver_test_flag0)
    self.assertEqual('unchanged0', FLAGS.flagsaver_test_flag0)

    # Decorator:
    @flagsaver_method(flagsaver_test_flag0='new value')
    def mutate_flags():
      self.assertEqual('new value', FLAGS.flagsaver_test_flag0)

    mutate_flags()
    self.assertEqual('unchanged0', FLAGS.flagsaver_test_flag0)

  def test_flagholder_overrides(self, flagsaver_method):
    with flagsaver_method((STR_FLAG, 'new value')):
      self.assertEqual('new value', STR_FLAG.value)
    self.assertEqual('str default', STR_FLAG.value)

    @flagsaver_method((STR_FLAG, 'new value'))
    def mutate_flags():
      self.assertEqual('new value', STR_FLAG.value)

    mutate_flags()
    self.assertEqual('str default', STR_FLAG.value)

  def test_keyword_and_flagholder_overrides(self, flagsaver_method):
    with flagsaver_method(
        (STR_FLAG, 'another value'), flagsaver_test_flag0='new value'
    ):
      self.assertEqual('another value', STR_FLAG.value)
      self.assertEqual('new value', FLAGS.flagsaver_test_flag0)
    self.assertEqual('str default', STR_FLAG.value)
    self.assertEqual('unchanged0', FLAGS.flagsaver_test_flag0)

    @flagsaver_method(
        (STR_FLAG, 'another value'), flagsaver_test_flag0='new value'
    )
    def mutate_flags():
      self.assertEqual('another value', STR_FLAG.value)
      self.assertEqual('new value', FLAGS.flagsaver_test_flag0)

    mutate_flags()
    self.assertEqual('str default', STR_FLAG.value)
    self.assertEqual('unchanged0', FLAGS.flagsaver_test_flag0)

  def test_cross_validated_overrides_set_together(self, flagsaver_method):
    # When the flags are set in the same flagsaver call their validators will
    # be triggered only once the setting is done.
    with flagsaver_method(
        flagsaver_test_validated_flag1='new_value',
        flagsaver_test_validated_flag2='new_value',
    ):
      self.assertEqual('new_value', FLAGS.flagsaver_test_validated_flag1)
      self.assertEqual('new_value', FLAGS.flagsaver_test_validated_flag2)
    self.assertIsNone(FLAGS.flagsaver_test_validated_flag1)
    self.assertIsNone(FLAGS.flagsaver_test_validated_flag2)

    @flagsaver_method(
        flagsaver_test_validated_flag1='new_value',
        flagsaver_test_validated_flag2='new_value',
    )
    def mutate_flags():
      self.assertEqual('new_value', FLAGS.flagsaver_test_validated_flag1)
      self.assertEqual('new_value', FLAGS.flagsaver_test_validated_flag2)

    mutate_flags()
    self.assertIsNone(FLAGS.flagsaver_test_validated_flag1)
    self.assertIsNone(FLAGS.flagsaver_test_validated_flag2)

  def test_cross_validated_overrides_set_badly(self, flagsaver_method):
    # Different values should violate the validator.
    with self.assertRaisesRegex(
        flags.IllegalFlagValueError, 'Flag validation failed'
    ):
      with flagsaver_method(
          flagsaver_test_validated_flag1='new_value',
          flagsaver_test_validated_flag2='other_value',
      ):
        pass
    self.assertIsNone(FLAGS.flagsaver_test_validated_flag1)
    self.assertIsNone(FLAGS.flagsaver_test_validated_flag2)

    @flagsaver_method(
        flagsaver_test_validated_flag1='new_value',
        flagsaver_test_validated_flag2='other_value',
    )
    def mutate_flags():
      pass

    self.assertRaisesRegex(
        flags.IllegalFlagValueError, 'Flag validation failed', mutate_flags
    )
    self.assertIsNone(FLAGS.flagsaver_test_validated_flag1)
    self.assertIsNone(FLAGS.flagsaver_test_validated_flag2)

  def test_cross_validated_overrides_set_separately(self, flagsaver_method):
    # Setting just one flag will trip the validator as well.
    with self.assertRaisesRegex(
        flags.IllegalFlagValueError, 'Flag validation failed'
    ):
      with flagsaver_method(flagsaver_test_validated_flag1='new_value'):
        pass
    self.assertIsNone(FLAGS.flagsaver_test_validated_flag1)
    self.assertIsNone(FLAGS.flagsaver_test_validated_flag2)

    @flagsaver_method(flagsaver_test_validated_flag1='new_value')
    def mutate_flags():
      pass

    self.assertRaisesRegex(
        flags.IllegalFlagValueError, 'Flag validation failed', mutate_flags
    )
    self.assertIsNone(FLAGS.flagsaver_test_validated_flag1)
    self.assertIsNone(FLAGS.flagsaver_test_validated_flag2)

  def test_validation_exception(self, flagsaver_method):
    with self.assertRaises(flags.IllegalFlagValueError):
      with flagsaver_method(
          flagsaver_test_flag0='new value',
          flagsaver_test_validated_flag='new value',
      ):
        pass
    self.assertEqual('unchanged0', FLAGS.flagsaver_test_flag0)
    self.assertIsNone(FLAGS.flagsaver_test_validated_flag)

    @flagsaver_method(
        flagsaver_test_flag0='new value',
        flagsaver_test_validated_flag='new value',
    )
    def mutate_flags():
      pass

    self.assertRaises(flags.IllegalFlagValueError, mutate_flags)
    self.assertEqual('unchanged0', FLAGS.flagsaver_test_flag0)
    self.assertIsNone(FLAGS.flagsaver_test_validated_flag)

  def test_unknown_flag_raises_exception(self, flagsaver_method):
    self.assertNotIn('this_flag_does_not_exist', FLAGS)

    # Flagsaver raises an error when trying to override a non-existent flag.
    with self.assertRaises(flags.UnrecognizedFlagError):
      with flagsaver_method(
          flagsaver_test_flag0='new value', this_flag_does_not_exist='new value'
      ):
        pass
    self.assertEqual('unchanged0', FLAGS.flagsaver_test_flag0)

    @flagsaver_method(
        flagsaver_test_flag0='new value', this_flag_does_not_exist='new value'
    )
    def mutate_flags():
      pass

    self.assertRaises(flags.UnrecognizedFlagError, mutate_flags)
    self.assertEqual('unchanged0', FLAGS.flagsaver_test_flag0)

    # Make sure flagsaver didn't create the flag at any point.
    self.assertNotIn('this_flag_does_not_exist', FLAGS)


class AsParsedTest(absltest.TestCase):

  def test_parse_context_manager_sets_present_and_using_default(self):
    self.assertFalse(INT_FLAG.present)
    self.assertFalse(STR_FLAG.present)
    # Note that .using_default_value isn't available on the FlagHolder directly.
    self.assertTrue(FLAGS[INT_FLAG.name].using_default_value)
    self.assertTrue(FLAGS[STR_FLAG.name].using_default_value)

    with flagsaver.as_parsed((INT_FLAG, '123'),
                             flagsaver_test_str_flag='new value'):
      self.assertTrue(INT_FLAG.present)
      self.assertTrue(STR_FLAG.present)
      self.assertFalse(FLAGS[INT_FLAG.name].using_default_value)
      self.assertFalse(FLAGS[STR_FLAG.name].using_default_value)

    self.assertFalse(INT_FLAG.present)
    self.assertFalse(STR_FLAG.present)
    self.assertTrue(FLAGS[INT_FLAG.name].using_default_value)
    self.assertTrue(FLAGS[STR_FLAG.name].using_default_value)

  def test_parse_decorator_sets_present_and_using_default(self):
    self.assertFalse(INT_FLAG.present)
    self.assertFalse(STR_FLAG.present)
    # Note that .using_default_value isn't available on the FlagHolder directly.
    self.assertTrue(FLAGS[INT_FLAG.name].using_default_value)
    self.assertTrue(FLAGS[STR_FLAG.name].using_default_value)

    @flagsaver.as_parsed((INT_FLAG, '123'), flagsaver_test_str_flag='new value')
    def some_func():
      self.assertTrue(INT_FLAG.present)
      self.assertTrue(STR_FLAG.present)
      self.assertFalse(FLAGS[INT_FLAG.name].using_default_value)
      self.assertFalse(FLAGS[STR_FLAG.name].using_default_value)

    some_func()
    self.assertFalse(INT_FLAG.present)
    self.assertFalse(STR_FLAG.present)
    self.assertTrue(FLAGS[INT_FLAG.name].using_default_value)
    self.assertTrue(FLAGS[STR_FLAG.name].using_default_value)

  def test_parse_decorator_with_multi_int_flag(self):
    self.assertFalse(MULTI_INT_FLAG.present)
    self.assertIsNone(MULTI_INT_FLAG.value)

    @flagsaver.as_parsed((MULTI_INT_FLAG, ['123', '456']))
    def assert_flags_updated():
      self.assertTrue(MULTI_INT_FLAG.present)
      self.assertCountEqual([123, 456], MULTI_INT_FLAG.value)

    assert_flags_updated()
    self.assertFalse(MULTI_INT_FLAG.present)
    self.assertIsNone(MULTI_INT_FLAG.value)

  def test_parse_raises_type_error(self):
    with self.assertRaisesRegex(
        TypeError,
        r'flagsaver\.as_parsed\(\) cannot parse flagsaver_test_int_flag\. '
        r'Expected a single string or sequence of strings but .*int.* was '
        r'provided\.'):
      manager = flagsaver.as_parsed(flagsaver_test_int_flag=123)  # pytype: disable=wrong-arg-types
      del manager


class SetUpTearDownTest(absltest.TestCase):
  """Example using a single flagsaver in setUp."""

  def setUp(self):
    super().setUp()
    self.saved_flag_values = flagsaver.save_flag_values()

  def tearDown(self):
    super().tearDown()
    flagsaver.restore_flag_values(self.saved_flag_values)

  def test_mutate1(self):
    # Even though other test cases change the flag, it should be
    # restored to 'unchanged0' if the flagsaver is working.
    self.assertEqual('unchanged0', FLAGS.flagsaver_test_flag0)
    FLAGS.flagsaver_test_flag0 = 'changed0'

  def test_mutate2(self):
    # Even though other test cases change the flag, it should be
    # restored to 'unchanged0' if the flagsaver is working.
    self.assertEqual('unchanged0', FLAGS.flagsaver_test_flag0)
    FLAGS.flagsaver_test_flag0 = 'changed0'


@parameterized.named_parameters(
    dict(
        testcase_name='flagsaver.flagsaver',
        flagsaver_method=flagsaver.flagsaver,
    ),
    dict(
        testcase_name='flagsaver.as_parsed',
        flagsaver_method=flagsaver.as_parsed,
    ),
)
class BadUsageTest(parameterized.TestCase):
  """Tests that improper usage (such as decorating a class) raise errors."""

  def test_flag_saver_on_class(self, flagsaver_method):
    with self.assertRaises(TypeError):

      # WRONG. Don't do this.
      # Consider the correct usage example in FlagSaverSetUpTearDownUsageTest.
      @flagsaver_method
      class FooTest(absltest.TestCase):

        def test_tautology(self):
          pass

      del FooTest

  def test_flag_saver_call_on_class(self, flagsaver_method):
    with self.assertRaises(TypeError):

      # WRONG. Don't do this.
      # Consider the correct usage example in FlagSaverSetUpTearDownUsageTest.
      @flagsaver_method()
      class FooTest(absltest.TestCase):

        def test_tautology(self):
          pass

      del FooTest

  def test_flag_saver_with_overrides_on_class(self, flagsaver_method):
    with self.assertRaises(TypeError):

      # WRONG. Don't do this.
      # Consider the correct usage example in FlagSaverSetUpTearDownUsageTest.
      @flagsaver_method(foo='bar')
      class FooTest(absltest.TestCase):

        def test_tautology(self):
          pass

      del FooTest

  def test_multiple_positional_parameters(self, flagsaver_method):
    with self.assertRaises(ValueError):
      func_a = lambda: None
      func_b = lambda: None
      flagsaver_method(func_a, func_b)

  def test_both_positional_and_keyword_parameters(self, flagsaver_method):
    with self.assertRaises(ValueError):
      func_a = lambda: None
      flagsaver_method(func_a, flagsaver_test_flag0='new value')

  def test_duplicate_holder_parameters(self, flagsaver_method):
    with self.assertRaises(ValueError):
      flagsaver_method((INT_FLAG, 45), (INT_FLAG, 45))

  def test_duplicate_holder_and_kw_parameter(self, flagsaver_method):
    with self.assertRaises(ValueError):
      flagsaver_method((INT_FLAG, 45), **{INT_FLAG.name: 45})

  def test_both_positional_and_holder_parameters(self, flagsaver_method):
    with self.assertRaises(ValueError):
      func_a = lambda: None
      flagsaver_method(func_a, (INT_FLAG, 45))

  def test_holder_parameters_wrong_shape(self, flagsaver_method):
    with self.assertRaises(ValueError):
      flagsaver_method(INT_FLAG)

  def test_holder_parameters_tuple_too_long(self, flagsaver_method):
    with self.assertRaises(ValueError):
      # Even if it is a bool flag, it should be a tuple
      flagsaver_method((INT_FLAG, 4, 5))

  def test_holder_parameters_tuple_wrong_type(self, flagsaver_method):
    with self.assertRaises(ValueError):
      # Even if it is a bool flag, it should be a tuple
      flagsaver_method((4, INT_FLAG))

  def test_both_wrong_positional_parameters(self, flagsaver_method):
    with self.assertRaises(ValueError):
      func_a = lambda: None
      flagsaver_method(func_a, STR_FLAG, '45')

  def test_context_manager_no_call(self, flagsaver_method):
    # The exact exception that's raised appears to be system specific.
    with self.assertRaises((AttributeError, TypeError)):
      # Wrong. You must call the flagsaver method before using it as a CM.
      with flagsaver_method:
        # We don't expect to get here. A type error should happen when
        # attempting to enter the context manager.
        pass


if __name__ == '__main__':
  absltest.main()
