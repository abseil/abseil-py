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

"""A Python test reporter that generates test reports in JUnit XML format."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import re
import sys
import threading
import time
import traceback
import unittest
from xml.sax import saxutils

from absl.third_party import unittest3_backport
import six


# See http://www.w3.org/TR/REC-xml/#NT-Char
_bad_control_character_codes = set(range(0, 0x20)) - {0x9, 0xA, 0xD}


_control_character_conversions = {
    chr(i): '\\x{:02x}'.format(i) for i in _bad_control_character_codes}


_escape_xml_attr_conversions = {
    '"': '&quot;',
    "'": '&apos;',
    '\n': '&#xA;',
    '\t': '&#x9;',
    '\r': '&#xD;',
    ' ': '&#x20;'}
_escape_xml_attr_conversions.update(_control_character_conversions)


# When class or module level function fails, unittest/suite.py adds a
# _ErrorHolder instance instead of a real TestCase, and it has a description
# like "setUpClass (__main__.MyTestCase)".
_CLASS_OR_MODULE_LEVEL_TEST_DESC_REGEX = re.compile(r'^(\w+) \((\S+)\)$')


# NOTE: while saxutils.quoteattr() theoretically does the same thing; it
# seems to often end up being too smart for it's own good not escaping properly.
# This function is much more reliable.
def _escape_xml_attr(content):
  """Escapes xml attributes."""
  # Note: saxutils doesn't escape the quotes.
  return saxutils.escape(content, _escape_xml_attr_conversions)


def _escape_cdata(s):
  """Escapes a string to be used as XML CDATA.

  CDATA characters are treated strictly as character data, not as XML markup,
  but there are still certain restrictions on them.

  Args:
    s: the string to be escaped.
  Returns:
    An escaped version of the input string.
  """
  for char, escaped in six.iteritems(_control_character_conversions):
    s = s.replace(char, escaped)
  return s.replace(']]>', ']] >')


# Copy time.time which ensures the real time is used internally.
# This prevents bad interactions with tests that stub out time.
_time_copy = time.time

if hasattr(traceback, '_some_str'):
  # Use the traceback module str function to format safely.
  _safe_str = traceback._some_str
else:
  _safe_str = str  # pylint: disable=invalid-name


class _TestCaseResult(object):
  """Private helper for _TextAndXMLTestResult that represents a test result.

  Attributes:
    test: A TestCase instance of an individual test method.
    name: The name of the individual test method.
    full_class_name: The full name of the test class.
    run_time: The duration (in seconds) it took to run the test.
    errors: A list of error 4-tuples. Error tuple entries are
        1) a string identifier of either "failure" or "error"
        2) an exception_type
        3) an exception_message
        4) a string version of a sys.exc_info()-style tuple of values
           ('error', err[0], err[1], self._exc_info_to_string(err))
           If the length of errors is 0, then the test is either passed or
           skipped.
    skip_reason: A string explaining why the test was skipped.
  """

  def __init__(self, test):
    self.run_time = -1
    self.skip_reason = None
    self.errors = []
    self.test = test

    # Parse the test id to get its test name and full class path.
    # Unfortunately there is no better way of knowning the test and class.
    # Worse, unittest uses _ErrorHandler instances to represent class / module
    # level failures.
    test_desc = test.id() or str(test)
    # Check if it's something like "setUpClass (__main__.TestCase)".
    match = _CLASS_OR_MODULE_LEVEL_TEST_DESC_REGEX.match(test_desc)
    if match:
      name = match.group(1)
      full_class_name = match.group(2)
    else:
      class_name = unittest.util.strclass(test.__class__)
      if six.PY3 and isinstance(test, unittest.case._SubTest):
        # subtest is introduced in Python3
        # If the test case is a _SubTest, the real TestCase instance is
        # available as _SubTest.test_case.
        class_name = unittest.util.strclass(test.test_case.__class__)

      if test_desc.startswith(class_name + '.'):
        # In a typical unittest.TestCase scenario, test.id() returns with
        # a class name formatted using unittest.util.strclass.
        name = test_desc[len(class_name)+1:]
        full_class_name = class_name
      else:
        # Otherwise make a best effort to guess the test name and full class
        # path.
        parts = test_desc.rsplit('.', 1)
        name = parts[-1]
        full_class_name = parts[0] if len(parts) == 2 else ''
    self.name = _escape_xml_attr(name)
    self.full_class_name = _escape_xml_attr(full_class_name)

  def set_run_time(self, time_in_secs):
    self.run_time = time_in_secs

  def print_xml_summary(self, stream):
    """Prints an XML Summary of a TestCase.

    Status and result are populated as per JUnit XML test result reporter.
    A test that has been skipped will always have a skip reason,
    as every skip method in Python's unittest requires the reason arg to be
    passed.

    Args:
      stream: output stream to write test report XML to
    """

    if self.skip_reason is None:
      status = 'run'
      result = 'completed'
    else:
      status = 'notrun'
      result = 'suppressed'

    stream.write(
        '  <testcase name="%s" status="%s" result="%s" time="%.1f" '
        'classname="%s">\n' % (
            self.name, status, result, self.run_time, self.full_class_name))
    self._print_testcase_details(stream)
    stream.write('  </testcase>\n')

  def _print_testcase_details(self, stream):
    for error in self.errors:
      outcome, exception_type, message, error_msg = error  # pylint: disable=unpacking-non-sequence
      message = _escape_xml_attr(_safe_str(message))
      exception_type = _escape_xml_attr(str(exception_type))
      error_msg = _escape_cdata(error_msg)
      stream.write('  <%s message="%s" type="%s"><![CDATA[%s]]></%s>\n'
                   % (outcome, message, exception_type, error_msg, outcome))


class _TestSuiteResult(object):
  """Private helper for _TextAndXMLTestResult."""

  def __init__(self):
    self.suites = {}
    self.failure_counts = {}
    self.error_counts = {}

  def add_test_case_result(self, test_case_result):
    suite_name = type(test_case_result.test).__name__
    if suite_name == '_ErrorHolder':
      # _ErrorHolder is a special case created by unittest for class / module
      # level functions.
      suite_name = test_case_result.full_class_name.rsplit('.')[-1]
    if six.PY3 and isinstance(test_case_result.test, unittest.case._SubTest):
      # subTest is introduced in Python3.
      # If the test case is a _SubTest, the real TestCase instance is
      # available as _SubTest.test_case.
      suite_name = type(test_case_result.test.test_case).__name__

    self._setup_test_suite(suite_name)
    self.suites[suite_name].append(test_case_result)
    for error in test_case_result.errors:
      # Only count the first failure or error so that the sum is equal to the
      # total number of *testcases* that have failures or errors.
      if error[0] == 'failure':
        self.failure_counts[suite_name] += 1
        break
      elif error[0] == 'error':
        self.error_counts[suite_name] += 1
        break

  def print_xml_summary(self, stream):
    overall_test_count = sum([len(x) for x in self.suites.values()])
    overall_failures = sum(self.failure_counts.values())
    overall_errors = sum(self.error_counts.values())
    overall_time = 0
    for tests in self.suites.values():
      overall_time += sum([x.run_time for x in tests])
    overall_args = (overall_test_count, overall_failures, overall_errors,
                    overall_time)
    stream.write('<testsuites name="" tests="%d" failures="%d" '
                 'errors="%d" time="%.1f">\n' % overall_args)
    for suite_name in self.suites:
      suite = self.suites[suite_name]
      suite_time = sum([x.run_time for x in suite])
      failures = self.failure_counts[suite_name]
      errors = self.error_counts[suite_name]
      args = (suite_name, len(suite), failures, errors, suite_time)
      stream.write('<testsuite name="%s" tests="%d" failures="%d" '
                   'errors="%d" time="%.1f">\n' % args)
      for test_case_result in suite:
        test_case_result.print_xml_summary(stream)
      stream.write('</testsuite>\n')
    stream.write('</testsuites>\n')

  def _setup_test_suite(self, suite_name):
    """Adds a test suite to the set of suites tracked by this test run.

    Args:
      suite_name: string, The name of the test suite being initialized.
    """
    if suite_name in self.suites:
      return
    self.suites[suite_name] = []
    self.failure_counts[suite_name] = 0
    self.error_counts[suite_name] = 0


class _TextAndXMLTestResult(unittest3_backport.TextTestResult):
  """Private TestResult class that produces both formatted text results and XML.

  Used by TextAndXMLTestRunner.
  """

  _TEST_SUITE_RESULT_CLASS = _TestSuiteResult
  _TEST_CASE_RESULT_CLASS = _TestCaseResult

  def __init__(self, xml_stream, stream, descriptions, verbosity,
               time_getter=_time_copy):
    super(_TextAndXMLTestResult, self).__init__(stream, descriptions, verbosity)
    self.xml_stream = xml_stream
    self.pending_test_case_results = {}
    self.suite = self._TEST_SUITE_RESULT_CLASS()
    self.time_getter = time_getter

    # This lock guards any mutations on pending_test_case_results.
    self._pending_test_case_results_lock = threading.Lock()

  def startTest(self, test):
    self.start_time = self.time_getter()
    super(_TextAndXMLTestResult, self).startTest(test)

  def stopTest(self, test):
    # Grabbing the write lock to avoid conflicting with stopTestRun.
    with self._pending_test_case_results_lock:
      super(_TextAndXMLTestResult, self).stopTest(test)
      result = self.get_pending_test_case_result(test)
      if not result:
        test_name = test.id() or str(test)
        sys.stderr.write('No pending test case: %s\n' % test_name)
        return
      test_id = id(test)
      run_time = self.time_getter() - self.start_time
      result.set_run_time(run_time)
      self.suite.add_test_case_result(result)
      del self.pending_test_case_results[test_id]

  def stopTestRun(self):
    # All pending_test_case_results will be added to the suite and removed from
    # the pending_test_case_results dictionary. Grabing the write lock to avoid
    # results from being added during this process to avoid duplicating adds or
    # accidentally erasing newly appended pending results.
    with self._pending_test_case_results_lock:
      # Errors in the test fixture (setUpModule, tearDownModule,
      # setUpClass, tearDownClass) can leave a pending result which
      # never gets added to the suite.  The runner calls stopTestRun
      # which gives us an opportunity to add these errors for
      # reporting here.
      for test_id in self.pending_test_case_results:
        result = self.pending_test_case_results[test_id]
        if hasattr(self, 'start_time'):
          run_time = self.time_getter() - self.start_time
          result.set_run_time(run_time)
        self.suite.add_test_case_result(result)
      self.pending_test_case_results.clear()

  def _exc_info_to_string(self, err, test=None):
    """Converts a sys.exc_info()-style tuple of values into a string.

    This method must be overridden because the method signature in
    unittest.TestResult changed between Python 2.2 and 2.4.

    Args:
      err: A sys.exc_info() tuple of values for an error.
      test: The test method.

    Returns:
      A formatted exception string.
    """
    if test:
      return super(_TextAndXMLTestResult, self)._exc_info_to_string(err, test)
    return ''.join(traceback.format_exception(*err))

  def add_pending_test_case_result(self, test, error_summary=None,
                                   skip_reason=None):
    """Adds result information to a test case result which may still be running.

    If a result entry for the test already exists, add_pending_test_case_result
    will add error summary tuples and/or overwrite skip_reason for the result.
    If it does not yet exist, a result entry will be created.
    Note that a test result is considered to have been run and passed
    only if there are no errors or skip_reason.

    Args:
      test: A test method as defined by unittest
      error_summary: A 4-tuple with the following entries:
          1) a string identifier of either "failure" or "error"
          2) an exception_type
          3) an exception_message
          4) a string version of a sys.exc_info()-style tuple of values
             ('error', err[0], err[1], self._exc_info_to_string(err))
             If the length of errors is 0, then the test is either passed or
             skipped.
      skip_reason: a string explaining why the test was skipped
    """
    with self._pending_test_case_results_lock:
      test_id = id(test)
      if test_id not in self.pending_test_case_results:
        self.pending_test_case_results[test_id] = self._TEST_CASE_RESULT_CLASS(
            test)
      if error_summary:
        self.pending_test_case_results[test_id].errors.append(error_summary)
      if skip_reason:
        self.pending_test_case_results[test_id].skip_reason = skip_reason

  def delete_pending_test_case_result(self, test):
    with self._pending_test_case_results_lock:
      test_id = id(test)
      del self.pending_test_case_results[test_id]

  def get_pending_test_case_result(self, test):
    test_id = id(test)
    return self.pending_test_case_results.get(test_id, None)

  def addSuccess(self, test):
    super(_TextAndXMLTestResult, self).addSuccess(test)
    self.add_pending_test_case_result(test)

  def addError(self, test, err):
    super(_TextAndXMLTestResult, self).addError(test, err)
    error_summary = ('error', err[0], err[1], self._exc_info_to_string(err))
    self.add_pending_test_case_result(test, error_summary=error_summary)

  def addFailure(self, test, err):
    super(_TextAndXMLTestResult, self).addFailure(test, err)
    error_summary = ('failure', err[0], err[1], self._exc_info_to_string(err))
    self.add_pending_test_case_result(test, error_summary=error_summary)

  def addSkip(self, test, reason):
    super(_TextAndXMLTestResult, self).addSkip(test, reason)
    self.add_pending_test_case_result(test, skip_reason=reason)

  def addExpectedFailure(self, test, err):
    super(_TextAndXMLTestResult, self).addExpectedFailure(test, err)
    if callable(getattr(test, 'recordProperty', None)):
      test.recordProperty('EXPECTED_FAILURE', self._exc_info_to_string(err))
    self.add_pending_test_case_result(test)

  def addUnexpectedSuccess(self, test):
    super(_TextAndXMLTestResult, self).addUnexpectedSuccess(test)
    test_name = test.id() or str(test)
    error_summary = ('error', '', '',
                     'Test case %s should have failed, but passed.'
                     % (test_name))
    self.add_pending_test_case_result(test, error_summary=error_summary)

  def addSubTest(self, test, subtest, err):  # pylint: disable=invalid-name
    super(_TextAndXMLTestResult, self).addSubTest(test, subtest, err)
    if err is not None:
      if issubclass(err[0], test.failureException):
        error_summary = ('failure', err[0], err[1],
                         self._exc_info_to_string(err))
      else:
        error_summary = ('error', err[0], err[1],
                         self._exc_info_to_string(err))
    else:
      error_summary = None
    self.add_pending_test_case_result(subtest, error_summary=error_summary)

  def printErrors(self):
    super(_TextAndXMLTestResult, self).printErrors()
    self.xml_stream.write('<?xml version="1.0"?>\n')
    self.suite.print_xml_summary(self.xml_stream)


class TextAndXMLTestRunner(unittest.TextTestRunner):
  """A test runner that produces both formatted text results and XML.

  It prints out the names of tests as they are run, errors as they
  occur, and a summary of the results at the end of the test run.
  """

  _TEST_RESULT_CLASS = _TextAndXMLTestResult

  _xml_stream = None

  def __init__(self, xml_stream=None, *args, **kwargs):
    """Initialize a TextAndXMLTestRunner.

    Args:
      xml_stream: file-like or None; XML-formatted test results are output
          via this object's write() method.  If None (the default), the
          new instance behaves as described in the set_default_xml_stream method
          documentation below.
      *args: passed unmodified to unittest.TextTestRunner.__init__.
      **kwargs: passed unmodified to unittest.TextTestRunner.__init__.
    """
    super(TextAndXMLTestRunner, self).__init__(*args, **kwargs)
    if xml_stream is not None:
      self._xml_stream = xml_stream
    # else, do not set self._xml_stream to None -- this allows implicit fallback
    # to the class attribute's value.

  @classmethod
  def set_default_xml_stream(cls, xml_stream):
    """Sets the default XML stream for the class.

    Args:
      xml_stream: file-like or None; used for instances when xml_stream is None
          or not passed to their constructors.  If None is passed, instances
          created with xml_stream=None will act as ordinary TextTestRunner
          instances; this is the default state before any calls to this method
          have been made.
    """
    cls._xml_stream = xml_stream

  def _makeResult(self):
    if self._xml_stream is None:
      return super(TextAndXMLTestRunner, self)._makeResult()
    else:
      return self._TEST_RESULT_CLASS(self._xml_stream, self.stream,
                                     self.descriptions, self.verbosity)
