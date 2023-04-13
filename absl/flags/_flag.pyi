# Copyright 2020 The Abseil Authors.
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

"""Contains type annotations for Flag class."""

import copy
import functools

from absl.flags import _argument_parser
from absl.flags import _validators_classes
import enum

from typing import Callable, Text, TypeVar, Generic, Iterable, Type, List, Optional, Any, Union, Sequence

_T = TypeVar('_T')
_ET = TypeVar('_ET', bound=enum.Enum)


class Flag(Generic[_T]):

  name: Text
  default: Optional[_T]
  default_unparsed: Union[Optional[_T], Text]
  default_as_str: Optional[Text]
  help: Text
  short_name: Text
  boolean: bool
  present: bool
  parser: _argument_parser.ArgumentParser[_T]
  serializer: _argument_parser.ArgumentSerializer[_T]
  allow_override: bool
  allow_override_cpp: bool
  allow_hide_cpp: bool
  using_default_value: bool
  allow_overwrite: bool
  allow_using_method_names: bool
  validators: List[_validators_classes.Validator]

  def __init__(self,
               parser: _argument_parser.ArgumentParser[_T],
               serializer: Optional[_argument_parser.ArgumentSerializer[_T]],
               name: Text,
               default: Union[Optional[_T], Text],
               help_string: Optional[Text],
               short_name: Optional[Text] = ...,
               boolean: bool = ...,
               allow_override: bool = ...,
               allow_override_cpp: bool = ...,
               allow_hide_cpp: bool = ...,
               allow_overwrite: bool = ...,
               allow_using_method_names: bool = ...) -> None:
    ...


  @property
  def value(self) -> Optional[_T]: ...

  def parse(self, argument: Union[_T, Text, None]) -> None: ...

  def unparse(self) -> None: ...

  def _parse(self, argument: Any) -> Any: ...

  def _serialize(self, value: Any) -> Text: ...

  def __deepcopy__(self, memo: dict) -> Flag: ...

  def _get_parsed_value_as_string(self, value: Optional[_T]) -> Optional[Text]:
    ...

  def serialize(self) -> Text: ...

  def flag_type(self) -> Text: ...


class BooleanFlag(Flag[bool]):
  def __init__(self,
               name: Text,
               default: Union[Optional[bool], Text],
               help: Optional[Text],
               short_name: Optional[Text]=None,
               **args: Any) -> None:
    ...



class EnumFlag(Flag[Text]):
  def __init__(self,
               name: Text,
               default: Union[Optional[Text], Text],
               help: Optional[Text],
               enum_values: Sequence[Text],
               short_name: Optional[Text] = ...,
               case_sensitive: bool = ...,
               **args: Any):
      ...



class EnumClassFlag(Flag[_ET]):

  def __init__(self,
               name: Text,
               default: Union[Optional[_ET], Text],
               help: Optional[Text],
               enum_class: Type[_ET],
               short_name: Optional[Text]=None,
               **args: Any):
    ...



class MultiFlag(Flag[List[_T]]):
  ...


class MultiEnumClassFlag(MultiFlag[_ET]):
  def __init__(self,
               name: Text,
               default: Union[Optional[List[_ET]], Text],
               help_string: Optional[Text],
               enum_class: Type[_ET],
               **args: Any):
    ...


