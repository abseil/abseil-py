"""Helpers for absl build rules."""

def py2py3_test_binary(name, **kwargs):
    """Create the same binary with different python versions for testing.

    Given `name`, `${name}_py2` and `${name}_py3` targets are created with
    `python_version` set to `PY2` and `PY3`, respectively. An alias named
    `name` is also created that uses a `select()` between the two underlying
    targets; this makes it easier to reference the binaries in consuming rules.

    Args:
        name: base name of the binaries. "_py2" and "_py3" suffixed targets
          will be created from it.
        **kwargs: additional args to pass onto py_binary.
    """
    kwargs["testonly"] = 1
    kwargs["srcs_version"] = "PY2AND3"
    if not kwargs.get("main"):
        if len(kwargs.get("srcs", [])) != 1:
            fail("py2py3_test_binary requires main or len(srcs)==1")
        kwargs["main"] = kwargs["srcs"][0]

    native.alias(name = name, actual = select({
        "//absl:py3_mode": name + "_py3",
        "//absl:py2_mode": name + "_py2",
    }))

    native.py_binary(
        name = name + "_py2",
        python_version = "PY2",
        **kwargs
    )
    native.py_binary(
        name = name + "_py3",
        python_version = "PY3",
        **kwargs
    )
