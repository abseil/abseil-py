load("@rules_python//python:py_binary.bzl", "py_binary")
load("@rules_python//python:py_library.bzl", "py_library")
load("@rules_python//python:py_test.bzl", "py_test")

package(default_visibility = ["//visibility:private"])

licenses(["notice"])

py_library(
    name = "absltest",
    srcs = ["absltest.py"],
    visibility = ["//visibility:public"],
    deps = [
        ":_pretty_print_reporter",
        ":xml_reporter",
        "//absl:app",
        "//absl/flags",
        "//absl/logging",
    ],
)

py_library(
    name = "flagsaver",
    srcs = ["flagsaver.py"],
    visibility = ["//visibility:public"],
    deps = [
        "//absl/flags",
    ],
)

py_library(
    name = "parameterized",
    srcs = [
        "parameterized.py",
    ],
    visibility = ["//visibility:public"],
    deps = [
        ":absltest",
    ],
)

py_library(
    name = "xml_reporter",
    srcs = ["xml_reporter.py"],
    visibility = ["//visibility:public"],
    deps = [
        ":_pretty_print_reporter",
    ],
)

py_library(
    name = "_bazelize_command",
    testonly = 1,
    srcs = ["_bazelize_command.py"],
    visibility = ["//:__subpackages__"],
    deps = [
        "//absl/flags",
    ],
)

py_library(
    name = "_pretty_print_reporter",
    srcs = ["_pretty_print_reporter.py"],
)

py_library(
    name = "tests/absltest_env",
    testonly = True,
    srcs = ["tests/absltest_env.py"],
)

py_test(
    name = "tests/absltest_filtering_test",
    size = "medium",
    srcs = ["tests/absltest_filtering_test.py"],
    data = [":tests/absltest_filtering_test_helper"],
    deps = [
        ":_bazelize_command",
        ":absltest",
        ":parameterized",
        ":tests/absltest_env",
        "//absl/logging",
    ],
)

py_binary(
    name = "tests/absltest_filtering_test_helper",
    testonly = 1,
    srcs = ["tests/absltest_filtering_test_helper.py"],
    deps = [
        ":absltest",
        ":parameterized",
        "//absl:app",
    ],
)

py_test(
    name = "tests/absltest_fail_fast_test",
    size = "small",
    srcs = ["tests/absltest_fail_fast_test.py"],
    data = [":tests/absltest_fail_fast_test_helper"],
    deps = [
        ":_bazelize_command",
        ":absltest",
        ":parameterized",
        ":tests/absltest_env",
        "//absl/logging",
    ],
)

py_binary(
    name = "tests/absltest_fail_fast_test_helper",
    testonly = 1,
    srcs = ["tests/absltest_fail_fast_test_helper.py"],
    deps = [
        ":absltest",
        "//absl:app",
    ],
)

py_test(
    name = "tests/absltest_randomization_test",
    size = "medium",
    srcs = ["tests/absltest_randomization_test.py"],
    data = [":tests/absltest_randomization_testcase"],
    deps = [
        ":_bazelize_command",
        ":absltest",
        ":parameterized",
        ":tests/absltest_env",
        "//absl/flags",
    ],
)

py_binary(
    name = "tests/absltest_randomization_testcase",
    testonly = 1,
    srcs = ["tests/absltest_randomization_testcase.py"],
    deps = [
        ":absltest",
    ],
)

py_test(
    name = "tests/absltest_sharding_test",
    size = "small",
    srcs = ["tests/absltest_sharding_test.py"],
    data = [
        ":tests/absltest_sharding_test_helper",
        ":tests/absltest_sharding_test_helper_no_tests",
    ],
    deps = [
        ":_bazelize_command",
        ":absltest",
        ":parameterized",
        ":tests/absltest_env",
    ],
)

py_binary(
    name = "tests/absltest_sharding_test_helper",
    testonly = 1,
    srcs = ["tests/absltest_sharding_test_helper.py"],
    deps = [":absltest"],
)

py_binary(
    name = "tests/absltest_sharding_test_helper_no_tests",
    testonly = 1,
    srcs = ["tests/absltest_sharding_test_helper_no_tests.py"],
    deps = [":absltest"],
)

py_test(
    name = "tests/absltest_test",
    size = "small",
    srcs = ["tests/absltest_test.py"],
    data = [
        ":tests/absltest_test_helper",
        ":tests/absltest_test_helper_skipped",
    ],
    deps = [
        ":_bazelize_command",
        ":absltest",
        ":parameterized",
        ":tests/absltest_env",
    ],
)

py_binary(
    name = "tests/absltest_test_helper",
    testonly = 1,
    srcs = ["tests/absltest_test_helper.py"],
    deps = [
        ":absltest",
        "//absl:app",
        "//absl/flags",
    ],
)

py_binary(
    name = "tests/absltest_test_helper_skipped",
    testonly = 1,
    srcs = ["tests/absltest_test_helper_skipped.py"],
    deps = [":absltest"],
)

py_test(
    name = "tests/flagsaver_test",
    srcs = ["tests/flagsaver_test.py"],
    deps = [
        ":absltest",
        ":flagsaver",
        ":parameterized",
        "//absl/flags",
    ],
)

py_test(
    name = "tests/parameterized_test",
    srcs = ["tests/parameterized_test.py"],
    deps = [
        ":absltest",
        ":parameterized",
    ],
)

py_test(
    name = "tests/xml_reporter_test",
    srcs = ["tests/xml_reporter_test.py"],
    data = [":tests/xml_reporter_helper_test"],
    deps = [
        ":_bazelize_command",
        ":absltest",
        ":parameterized",
        ":xml_reporter",
        "//absl/logging",
    ],
)

py_binary(
    name = "tests/xml_reporter_helper_test",
    testonly = 1,
    srcs = ["tests/xml_reporter_helper_test.py"],
    deps = [
        ":absltest",
        "//absl/flags",
    ],
)
