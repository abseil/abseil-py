# Abseil Python Common Libraries

This repository is a collection of Python library code for building Python
applications. The code is collected from Google's own Python code base, and has
been extensively tested and used in production.

## Features

* Simple application startup
* Distributed commandline flags system
* Custom logging module with additional features
* Testing utilities

## Getting Started

### Installation

To install the package, simply run:

```bash
pip install absl-py
```

Or install from source:

```bash
python setup.py install
```

### Running Tests

To run Abseil tests, you can clone the git repo and run
[bazel](https://bazel.build/):

```bash
git clone git@github.com:abseil/abseil-py.git
cd abseil-py
bazel test absl/...
```

### Example Code

Please refer to [smoke_tests/sample_app.py](smoke_tests/sample_app.py) as an
example to get started.

## Documentation

Full documentation is forthcoming on https://abseil.io. For now, please refer
to the in-code Python docstrings.

## Future Releases

The current repository includes an initial set of libraries for early adoption.
More components and interoperability with Abseil C++ Common Libraries
will come in future releases.

## License

The Abseil Python library is licensed under the terms of the Apache
license. See [LICENSE](LICENSE) for more information.
