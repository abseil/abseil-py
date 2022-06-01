# Python Absl Changelog

All notable changes to Python Absl are recorded here.

The format is based on [Keep a Changelog](https://keepachangelog.com).

## Unreleased

Nothing notable unreleased.

## 1.1.0 (2022-06-01)

*   `Flag` instances now raise an error if used in a bool context. This prevents
    the occasional mistake of testing an instance for truthiness rather than
    testing `flag.value`.
*   `absl-py` no longer depends on `six`.

## 1.0.0 (2021-11-09)

### Changed

*   `absl-py` no longer supports Python 2.7, 3.4, 3.5. All versions have reached
    end-of-life for more than a year now.
*   New releases will be tagged as `vX.Y.Z` instead of `pypi-vX.Y.Z` in the git
    repo going forward.

## 0.15.0 (2021-10-19)

### Changed

*   (testing) #128: When running bazel with its `--test_filter=` flag, it now
    treats the filters as `unittest`'s `-k` flag in Python 3.7+.

## 0.14.1 (2021-09-30)

### Fixed

*   Top-level `LICENSE` file is now exported in bazel.

## 0.14.0 (2021-09-21)

### Fixed

*   #171: Creating `argparse_flags.ArgumentParser` with `argument_default=` no
    longer raises an exception when other `absl.flags` flags are defined.
*   #173: `absltest` now correctly sets up test filtering and fail fast flags
    when an explicit `argv=` parameter is passed to `absltest.main`.

## 0.13.0 (2021-06-14)

### Added

*   (app) Type annotations for public `app` interfaces.
*   (testing) Added new decorator `@absltest.skipThisClass` to indicate a class
    contains shared functionality to be used as a base class for other
    TestCases, and therefore should be skipped.

### Changed

*   (app) Annotated the `flag_parser` paramteter of `run` as keyword-only. This
    keyword-only constraint will be enforced at runtime in a future release.
*   (app, flags) Flag validations now include all errors from disjoint flag
    sets, instead of fail fast upon first error from all validators. Multiple
    validators on the same flag still fails fast.

## 0.12.0 (2021-03-08)

### Added

*   (flags) Made `EnumClassSerializer` and `EnumClassListSerializer` public.
*   (flags) Added a `required: Optional[bool] = False` parameter to `DEFINE_*`
    functions.
*   (testing) flagsaver overrides can now be specified in terms of FlagHolder.
*   (testing) `parameterized.product`: Allows testing a method over cartesian
    product of parameters values, specified as a sequences of values for each
    parameter or as kwargs-like dicts of parameter values.
*   (testing) Added public flag holders for `--test_srcdir` and `--test_tmpdir`.
    Users should use `absltest.TEST_SRCDIR.value` and
    `absltest.TEST_TMPDIR.value` instead of `FLAGS.test_srcdir` and
    `FLAGS.test_tmpdir`.

### Fixed

*   (flags) Made `CsvListSerializer` respect its delimiter argument.

## 0.11.0 (2020-10-27)

### Changed

*   (testing) Surplus entries in AssertionError stack traces from absltest are
    now suppressed and no longer reported in the xml_reporter.
*   (logging) An exception is now raised instead of `logging.fatal` when logging
    directories cannot be found.
*   (testing) Multiple flags are now set together before their validators run.
    This resolves an issue where multi-flag validators rely on specific flag
    combinations.
*   (flags) As a deterrent for misuse, FlagHolder objects will now raise a
    TypeError exception when used in a conditional statement or equality
    expression.

## 0.10.0 (2020-08-19)

### Added

*   (testing) `_TempDir` and `_TempFile` now implement `__fspath__` to satisfy
    `os.PathLike`
*   (logging) `--logger_levels`: allows specifying the log levels of loggers.
*   (flags) `FLAGS.validate_all_flags`: a new method that validates all flags
    and raises an exception if one fails.
*   (flags) `FLAGS.get_flags_for_module`: Allows fetching the flags a module
    defines.
*   (testing) `parameterized.TestCase`: Supports async test definitions.
*   (testing,app) Added `--pdb` flag: When true, uncaught exceptions will be
    handled by `pdb.post_mortem`. This is an alias for `--pdb_post_mortem`.

### Changed

*   (testing) Failed tests output a copy/pastable test id to make it easier to
    copy the failing test to the command line.
*   (testing) `@parameterized.parameters` now treats a single `abc.Mapping` as a
    single test case, consistent with `named_parameters`. Previously the
    `abc.Mapping` is treated as if only its keys are passed as a list of test
    cases. If you were relying on the old inconsistent behavior, explicitly
    convert the `abc.Mapping` to a `list`.
*   (flags) `DEFINE_enum_class` and `DEFINE_mutlti_enum_class` accept a
    `case_sensitive` argument. When `False` (the default), strings are mapped to
    enum member names without case sensitivity, and member names are serialized
    in lowercase form. Flag definitions for enums whose members include
    duplicates when case is ignored must now explicitly pass
    `case_sensitive=True`.

### Fixed

*   (flags) Defining an alias no longer marks the aliased flag as always present
    on the command line.
*   (flags) Aliasing a multi flag no longer causes the default value to be
    appended to.
*   (flags) Alias default values now matched the aliased default value.
*   (flags) Alias `present` counter now correctly reflects command line usage.

## 0.9.0 (2019-12-17)

### Added

*   (testing) `TestCase.enter_context`: Allows using context managers in setUp
    and having them automatically exited when a test finishes.

### Fixed

*   #126: calling `logging.debug(msg, stack_info=...)` no longer throws an
    exception in Python 3.8.

## 0.8.1 (2019-10-08)

### Fixed

*   (testing) `absl.testing`'s pretty print reporter no longer buffers
    RUN/OK/FAILED messages.
*   (testing) `create_tempfile` will overwrite pre-existing read-only files.

## 0.8.0 (2019-08-26)

### Added

*   (testing) `absltest.expectedFailureIf`: a variant of
    `unittest.expectedFailure` that allows a condition to be given.

### Changed

*   (bazel) Tests now pass when bazel
    `--incompatible_allow_python_version_transitions=true` is set.
*   (bazel) Both Python 2 and Python 3 versions of tests are now created. To
    only run one major Python version, use `bazel test
    --test_tag_filters=-python[23]` to ignore the other version.
*   (testing) `assertTotallyOrdered` no longer requires objects to implement
    `__hash__`.
*   (testing) `absltest` now integrates better with `--pdb_post_mortem`.
*   (testing) `xml_reporter` now includes timestamps to testcases, test_suite,
    test_suites elements.

### Fixed

*   #99: `absl.logging` no longer registers itself to `logging.root` at import
    time.
*   #108: Tests now pass with Bazel 0.28.0 on macOS.

## 0.7.1 (2019-03-12)

### Added

*   (flags) `flags.mark_bool_flags_as_mutual_exclusive`: convenience function to
    check that only one, or at most one, flag among a set of boolean flags are
    True.

### Changed

*   (bazel) Bazel 0.23+ or 0.22+ is now required for building/testing.
    Specifically, a Bazel version that supports
    `@bazel_tools//tools/python:python_version` for selecting the Python
    version.

### Fixed

*   #94: LICENSE files are now included in sdist.
*   #93: Change log added.

## 0.7.0 (2019-01-11)

### Added

*   (bazel) testonly=1 has been removed from the testing libraries, which allows
    their use outside of testing contexts.
*   (flags) Multi-flags now accept any Iterable type for the default value
    instead of only lists. Strings are still special cased as before. This
    allows sets, generators, views, etc to be used naturally.
*   (flags) DEFINE_multi_enum_class: a multi flag variant of enum_class.
*   (testing) Most of absltest is now type-annotated.
*   (testing) Made AbslTest.assertRegex available under Python 2. This allows
    Python 2 code to write more natural Python 3 compatible code. (Note: this
    was actually released in 0.6.1, but unannounced)
*   (logging) logging.vlog_is_on: helper to tell if a vlog() call will actually
    log anything. This allows avoiding computing expansive inputs to a logging
    call when logging isn't enabled for that level.

### Fixed

*   (flags) Pickling flags now raises an clear error instead of a cryptic one.
    Pickling flags isn't supported; instead use flags_into_string to serialize
    flags.
*   (flags) Flags serialization works better: the resulting serialized value,
    when deserialized, won't cause --help to be invoked, thus ending the
    process.
*   (flags) Several flag fixes to make them behave more like the Absl C++ flags:
    empty --flagfile is allowed; --nohelp and --help=false don't display help
*   (flags) An empty --flagfile value (e.g. "--flagfile=" or "--flagfile=''"
    doesn't raise an error; its not just ignored. This matches Abseil C++
    behavior.
*   (bazel) Building with Bazel 0.2.0 works without extra incompatibility disable
    build flags.

### Changed

*   (flags) Flag serialization is now deterministic: this improves Bazel build
    caching for tools that are affected by flag serialization.

## 0.6.0 (2018-10-22)

### Added

*   Tempfile management APIs for tests: read/write/manage tempfiles for test
    purposes easily and correctly. See TestCase.create_temp{file/dir} and the
    corresponding commit for more info.

## 0.5.0 (2018-09-17)

### Added

*   Flags enum support: flags.DEFINE_enum_class allows using an `Enum` derived
    class to define the allowed values for a flag.

## 0.4.1 (2018-08-28)

### Fixed

*   Flags no long allow spaces in their names

### Changed

*   XML test output is written at the end of all test execution.
*   If the current user's username can't be gotten, fallback to uid, else fall
    back to a generic 'unknown' string.

## 0.4.0 (2018-08-14)

### Added

*   argparse integration: absl-registered flags can now be accessed via argparse
    using absl.flags.argparse_flags: see that module for more information.
*   TestCase.assertSameStructure now allows mixed set types.

### Changed

*   Test output now includes start/end markers for each test ran. This is to
    help distinguish output from tests clearly.

## 0.3.0 (2018-07-25)

### Added

*   `app.call_after_init`: Register functions to be called after app.run() is
    called. Useful for program-wide initialization that library code may need.
*   `logging.log_every_n_seconds`: like log_every_n, but based on elapsed time
    between logging calls.
*   `absltest.mock`: alias to unittest.mock (PY3) for better unittest drop-in
    replacement. For PY2, it will be available if mock is importable.

### Fixed

*   `ABSLLogger.findCaller()`: allow stack_info arg and return value for PY2
*   Make stopTest locking reentrant: this prevents deadlocks for test frameworks
    that customize unittest.TextTestResult.stopTest.
*   Make --helpfull work with unicode flag help strings.
