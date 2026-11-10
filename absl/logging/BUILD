load("@rules_cc//cc:cc_library.bzl", "cc_library")
load("@rules_python//python:py_binary.bzl", "py_binary")
load("@rules_python//python:py_library.bzl", "py_library")
load("@rules_python//python:py_test.bzl", "py_test")

package(default_visibility = ["//visibility:private"])

licenses(["notice"])

py_library(
    name = "logging",
    srcs = ["__init__.py"],
    pyi_srcs = ["__init__.pyi"],
    visibility = ["//visibility:public"],
    deps = [
        ":converter",
        "//absl/flags",
    ],
)

py_library(
    name = "converter",
    srcs = ["converter.py"],
    visibility = ["//visibility:public"],
)

py_test(
    name = "tests/converter_test",
    size = "small",
    srcs = ["tests/converter_test.py"],
    deps = [
        ":converter",
        ":logging",
        "//absl/testing:absltest",
        "//absl/testing:parameterized",
    ],
)

py_test(
    name = "tests/logging_test",
    size = "small",
    srcs = ["tests/logging_test.py"],
    main = "tests/logging_test.py",
    pyi_deps = [
        "//base/python:pywrapbase",
    ],
    deps = [
        ":logging",
        "//absl/flags",
        "//absl/testing:absltest",
        "//absl/testing:flagsaver",
        "//absl/testing:parameterized",
    ],
)

py_test(
    name = "tests/log_before_import_test",
    srcs = ["tests/log_before_import_test.py"],
    main = "tests/log_before_import_test.py",
    deps = [
        ":logging",
        "//absl/testing:absltest",
    ],
)

py_test(
    name = "tests/verbosity_flag_test",
    srcs = ["tests/verbosity_flag_test.py"],
    deps = [
        ":logging",
        "//absl/flags",
        "//absl/testing:absltest",
    ],
)

py_binary(
    name = "tests/logging_functional_test_helper",
    testonly = 1,
    srcs = ["tests/logging_functional_test_helper.py"],
    main = "tests/logging_functional_test_helper.py",
    pyi_deps = [
        "//base/python:pywrapbase",
        "//third_party/py/absl/logging/tests/python:logging_functional_test_cpp_helper",
    ],
    deps = [
        ":logging",
        "//absl:app",
        "//absl/flags",
    ],
)

py_test(
    name = "tests/logging_functional_test",
    size = "large",
    srcs = ["tests/logging_functional_test.py"],
    data = [":tests/logging_functional_test_helper"],
    main = "tests/logging_functional_test.py",
    shard_count = 50,
    deps = [
        ":logging",
        "//absl/testing:_bazelize_command",
        "//absl/testing:absltest",
        "//absl/testing:parameterized",
    ],
)
