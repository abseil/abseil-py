load("@rules_cc//cc:cc_library.bzl", "cc_library")
load("@rules_python//python:py_binary.bzl", "py_binary")
load("@rules_python//python:py_library.bzl", "py_library")
load("@rules_python//python:py_test.bzl", "py_test")

package(default_visibility = ["//visibility:private"])

licenses(["notice"])

py_library(
    name = "flags",
    srcs = ["__init__.py"],
    visibility = ["//visibility:public"],
    deps = [
        ":_argument_parser",
        ":_defines",
        ":_exceptions",
        ":_flag",
        ":_flagvalues",
        ":_helpers",
        ":_validators",
    ],
)

py_library(
    name = "argparse_flags",
    srcs = ["argparse_flags.py"],
    visibility = ["//visibility:public"],
    deps = [":flags"],
)

py_library(
    name = "_argument_parser",
    srcs = ["_argument_parser.py"],
    deps = [
        ":_helpers",
    ],
)

py_library(
    name = "_defines",
    srcs = ["_defines.py"],
    deps = [
        ":_argument_parser",
        ":_exceptions",
        ":_flag",
        ":_flagvalues",
        ":_helpers",
        ":_validators",
    ],
)

py_library(
    name = "_exceptions",
    srcs = ["_exceptions.py"],
    deps = [
        ":_helpers",
    ],
)

py_library(
    name = "_flag",
    srcs = ["_flag.py"],
    deps = [
        ":_argument_parser",
        ":_exceptions",
        ":_helpers",
    ],
)

py_library(
    name = "_flagvalues",
    srcs = ["_flagvalues.py"],
    deps = [
        ":_exceptions",
        ":_flag",
        ":_helpers",
        ":_validators_classes",
    ],
)

py_library(
    name = "_helpers",
    srcs = ["_helpers.py"],
)

py_library(
    name = "_validators",
    srcs = [
        "_validators.py",
    ],
    deps = [
        ":_exceptions",
        ":_flagvalues",
        ":_validators_classes",
    ],
)

py_library(
    name = "_validators_classes",
    srcs = [
        "_validators_classes.py",
    ],
    deps = [
        ":_exceptions",
    ],
)

py_test(
    name = "tests/_argument_parser_test",
    srcs = ["tests/_argument_parser_test.py"],
    deps = [
        ":_argument_parser",
        "//absl/testing:absltest",
        "//absl/testing:parameterized",
    ],
)

py_test(
    name = "tests/_flag_test",
    srcs = ["tests/_flag_test.py"],
    deps = [
        ":_argument_parser",
        ":_exceptions",
        ":_flag",
        "//absl/testing:absltest",
        "//absl/testing:parameterized",
    ],
)

py_test(
    name = "tests/_flagvalues_test",
    size = "small",
    srcs = ["tests/_flagvalues_test.py"],
    deps = [
        ":_defines",
        ":_exceptions",
        ":_flagvalues",
        ":_helpers",
        ":_validators",
        ":tests/module_foo",
        "//absl/logging",
        "//absl/testing:absltest",
        "//absl/testing:parameterized",
    ],
)

py_test(
    name = "tests/_helpers_test",
    size = "small",
    srcs = ["tests/_helpers_test.py"],
    deps = [
        ":_helpers",
        ":tests/module_bar",
        ":tests/module_foo",
        "//absl/testing:absltest",
    ],
)

py_test(
    name = "tests/_validators_test",
    size = "small",
    srcs = ["tests/_validators_test.py"],
    deps = [
        ":_defines",
        ":_exceptions",
        ":_flagvalues",
        ":_validators",
        "//absl/testing:absltest",
    ],
)

py_test(
    name = "tests/argparse_flags_test",
    size = "small",
    srcs = ["tests/argparse_flags_test.py"],
    data = [":tests/argparse_flags_test_helper"],
    deps = [
        ":argparse_flags",
        ":flags",
        "//absl/logging",
        "//absl/testing:_bazelize_command",
        "//absl/testing:absltest",
        "//absl/testing:parameterized",
    ],
)

py_binary(
    name = "tests/argparse_flags_test_helper",
    testonly = 1,
    srcs = ["tests/argparse_flags_test_helper.py"],
    deps = [
        ":argparse_flags",
        ":flags",
        "//absl:app",
    ],
)

py_test(
    name = "tests/flags_formatting_test",
    size = "small",
    srcs = ["tests/flags_formatting_test.py"],
    deps = [
        ":_helpers",
        ":flags",
        "//absl/testing:absltest",
    ],
)

py_test(
    name = "tests/flags_helpxml_test",
    size = "small",
    srcs = ["tests/flags_helpxml_test.py"],
    deps = [
        ":_helpers",
        ":flags",
        ":tests/module_bar",
        "//absl/testing:absltest",
    ],
)

py_test(
    name = "tests/flags_numeric_bounds_test",
    size = "small",
    srcs = ["tests/flags_numeric_bounds_test.py"],
    deps = [
        ":_validators",
        ":flags",
        "//absl/testing:absltest",
    ],
)

py_test(
    name = "tests/flags_test",
    size = "small",
    srcs = ["tests/flags_test.py"],
    deps = [
        ":_exceptions",
        ":_helpers",
        ":flags",
        ":tests/module_bar",
        ":tests/module_baz",
        ":tests/module_foo",
        "//absl/testing:absltest",
    ],
)

py_test(
    name = "tests/flags_unicode_literals_test",
    size = "small",
    srcs = ["tests/flags_unicode_literals_test.py"],
    deps = [
        ":flags",
        "//absl/testing:absltest",
    ],
)

py_library(
    name = "tests/module_bar",
    testonly = 1,
    srcs = ["tests/module_bar.py"],
    deps = [
        ":_helpers",
        ":flags",
    ],
)

py_library(
    name = "tests/module_baz",
    testonly = 1,
    srcs = ["tests/module_baz.py"],
    deps = [":flags"],
)

py_library(
    name = "tests/module_foo",
    testonly = 1,
    srcs = ["tests/module_foo.py"],
    deps = [
        ":_helpers",
        ":flags",
        ":tests/module_bar",
    ],
)
