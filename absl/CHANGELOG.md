# Python Absl Changelog

All notable changes to Python Absl are recorded here.

The format is based on [Keep a Changelog](https://keepachangelog.com).

## Unreleased

Nothing notable unreleased.

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
*   (testing) `@parameterized.parameters` now treats a single `abc.Mapping` as
    a single test case, consistent with `named_parameters`. Previously the
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
*   (bazel) Building with Bazel 0.2.0 works without extra incompatiblity disable
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
