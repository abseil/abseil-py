# Copyright 2017 The Abseil Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
workspace(name = "io_abseil_py")

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

http_archive(
    name = "rules_cc",
    sha256 = "458b658277ba51b4730ea7a2020efdf1c6dcadf7d30de72e37f4308277fa8c01",
    strip_prefix = "rules_cc-0.2.16",
    url = "https://github.com/bazelbuild/rules_cc/releases/download/0.2.16/rules_cc-0.2.16.tar.gz",
)

http_archive(
    name = "rules_python",
    sha256 = "7ae25c0d3b52124fffe199a34520f43e496f4027d59452df70184eced23b96ef",
    strip_prefix = "rules_python-1.8.1",
    url = "https://github.com/bazel-contrib/rules_python/releases/download/1.8.1/rules_python-1.8.1.tar.gz",
)

load("@rules_python//python:repositories.bzl", "py_repositories")

py_repositories()
