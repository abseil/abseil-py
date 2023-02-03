licenses(["notice"])

py_library(
    name = "app",
    srcs = [
        "app.py",
    ],
    srcs_version = "PY2AND3",
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
    srcs_version = "PY2AND3",
    visibility = ["//visibility:public"],
)

py_library(
    name = "tests/app_test_helper",
    testonly = 1,
    srcs = ["tests/app_test_helper.py"],
    srcs_version = "PY2AND3",
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
    python_version = "PY3",
    srcs_version = "PY3",
    deps = [
        ":app",
        "//absl/flags",
    ],
)

py_test(
    name = "tests/app_test",
    srcs = ["tests/app_test.py"],
    data = [":tests/app_test_helper_pure_python"],
    python_version = "PY3",
    srcs_version = "PY3",
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
    python_version = "PY3",
    srcs_version = "PY3",
    deps = [
        ":command_name",
        "//absl/testing:absltest",
    ],
)

py_test(
    name = "tests/python_version_test",
    srcs = ["tests/python_version_test.py"],
    python_version = "PY3",
    srcs_version = "PY3",
    deps = [
        "//absl/flags",
        "//absl/testing:absltest",
    ],
)
