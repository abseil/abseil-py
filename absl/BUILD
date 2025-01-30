load("@rules_python//python:py_binary.bzl", "py_binary")
load("@rules_python//python:py_library.bzl", "py_library")
load("@rules_python//python:py_test.bzl", "py_test")

licenses(["notice"])

py_library(
    name = "app",
    srcs = [
        "app.py",
    ],
    visibility = ["//visibility:public"],
    deps = [
        ":command_name",
        "//absl/flags",
        "//absl/logging",
    ],
)

py_library(
    name = "command_name",
    srcs = ["command_name.py"],
    visibility = ["//visibility:public"],
)

py_library(
    name = "tests/app_test_helper",
    testonly = 1,
    srcs = ["tests/app_test_helper.py"],
    deps = [
        ":app",
        "//absl/flags",
    ],
)

py_binary(
    name = "tests/app_test_helper_pure_python",
    testonly = 1,
    srcs = ["tests/app_test_helper.py"],
    main = "tests/app_test_helper.py",
    deps = [
        ":app",
        "//absl/flags",
    ],
)

py_test(
    name = "tests/app_test",
    srcs = ["tests/app_test.py"],
    data = [":tests/app_test_helper_pure_python"],
    deps = [
        ":app",
        ":tests/app_test_helper",
        "//absl/flags",
        "//absl/testing:_bazelize_command",
        "//absl/testing:absltest",
        "//absl/testing:flagsaver",
    ],
)

py_test(
    name = "tests/command_name_test",
    srcs = ["tests/command_name_test.py"],
    deps = [
        ":command_name",
        "//absl/testing:absltest",
    ],
)

py_test(
    name = "tests/python_version_test",
    srcs = ["tests/python_version_test.py"],
    deps = [
        "//absl/flags",
        "//absl/testing:absltest",
    ],
)
