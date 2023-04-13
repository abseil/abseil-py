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

from xml.dom import minidom
import types
from typing import Any, Dict, Iterable, List, NamedTuple, Optional, Set

disclaim_module_ids: Set[int]
FLAGS_MODULE: types.ModuleType
# NOTE: This cannot be annotated as its actual FlagValues type since this would
# create a circular dependency.
SPECIAL_FLAGS: Any


class _ModuleObjectAndName(NamedTuple):
  module: types.ModuleType
  module_name: str


def get_module_object_and_name(
    globals_dict: Dict[str, Any]
) -> _ModuleObjectAndName:
  ...


def get_calling_module_object_and_name() -> _ModuleObjectAndName:
  ...


def get_calling_module() -> str:
  ...


def create_xml_dom_element(
    doc: minidom.Document, name: str, value: Any
) -> minidom.Element:
  ...


def get_help_width() -> int:
  ...


def get_flag_suggestions(
    attempt: Optional[str], longopt_list: List[str]
) -> List[str]:
  ...


def text_wrap(
    text: str,
    length: Optional[int] = ...,
    indent: str = ...,
    firstline_indent: Optional[str] = ...,
) -> str:
  ...


def flag_dict_to_args(
    flag_map: Dict[str, str], multi_flags: Optional[Set[str]] = ...
) -> Iterable[str]:
  ...


def trim_docstring(docstring: str) -> str:
  ...


def doc_to_help(doc: str) -> str:
  ...
