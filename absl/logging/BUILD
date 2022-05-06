licenses(["notice"])

py_library(
    name = "logging",
    srcs = ["__init__.py"],
    srcs_version = "PY2AND3",
    visibility = ["//visibility:public"],
    deps = [
        ":converter",
        "//absl/flags",
    ],
)

py_library(
    name = "converter",
    srcs = ["converter.py"],
    srcs_version = "PY2AND3",
    visibility = ["//visibility:public"],
)

py_test(
    name = "tests/converter_test",
    size = "small",
    srcs = ["tests/converter_test.py"],
    python_version = "PY3",
    srcs_version = "PY3",
    deps = [
        ":converter",
        ":logging",
        "//absl/testing:absltest",
    ],
)

py_test(
    name = "tests/logging_test",
    size = "small",
    srcs = ["tests/logging_test.py"],
    python_version = "PY3",
    srcs_version = "PY3",
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
    python_version = "PY3",
    srcs_version = "PY3",
    deps = [
        ":logging",
        "//absl/testing:absltest",
    ],
)

py_test(
    name = "tests/verbosity_flag_test",
    srcs = ["tests/verbosity_flag_test.py"],
    python_version = "PY3",
    srcs_version = "PY3",
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
    python_version = "PY3",
    srcs_version = "PY3",
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
    python_version = "PY3",
    shard_count = 50,
    srcs_version = "PY3",
    deps = [
        ":logging",
        "//absl/testing:_bazelize_command",
        "//absl/testing:absltest",
        "//absl/testing:parameterized",
    ],
)
