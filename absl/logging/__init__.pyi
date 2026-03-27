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

from collections.abc import Callable, Mapping
import logging
import types
import typing
from typing import Any, NoReturn, TypeAlias, TypeVar

from absl import flags

_ExcInfo: TypeAlias = (
    None
    | bool
    | tuple[type[BaseException], BaseException, types.TracebackType | None]
    | tuple[None, None, None]
    | BaseException
)

# Logging levels.
FATAL: int
ERROR: int
WARNING: int
WARN: int  # Deprecated name.
INFO: int
DEBUG: int

ABSL_LOGGING_PREFIX_REGEX: str

LOGTOSTDERR: flags.FlagHolder[bool]
ALSOLOGTOSTDERR: flags.FlagHolder[bool]
LOG_DIR: flags.FlagHolder[str]
VERBOSITY: flags.FlagHolder[int]
LOGGER_LEVELS: flags.FlagHolder[dict[str, str]]
STDERRTHRESHOLD: flags.FlagHolder[str]
SHOWPREFIXFORINFO: flags.FlagHolder[bool]

_ABSL_LOG_FATAL: str

def get_verbosity() -> int:
  ...

def set_verbosity(v: int | str) -> None:
  ...

def set_stderrthreshold(s: int | str) -> None:
  ...

def fatal(
    msg: object,
    *args: object,
    exc_info: _ExcInfo = ...,
    stack_info: bool = ...,
    stacklevel: int = ...,
    extra: Mapping[str, object] | None = ...,
) -> NoReturn:
  ...

def error(
    msg: object,
    *args: object,
    exc_info: _ExcInfo = ...,
    stack_info: bool = ...,
    stacklevel: int = ...,
    extra: Mapping[str, object] | None = ...,
) -> None:
  ...

def warning(
    msg: object,
    *args: object,
    exc_info: _ExcInfo = ...,
    stack_info: bool = ...,
    stacklevel: int = ...,
    extra: Mapping[str, object] | None = ...,
) -> None:
  ...

def warn(
    msg: object,
    *args: object,
    exc_info: _ExcInfo = ...,
    stack_info: bool = ...,
    stacklevel: int = ...,
    extra: Mapping[str, object] | None = ...,
) -> None:
  ...

def info(
    msg: object,
    *args: object,
    exc_info: _ExcInfo = ...,
    stack_info: bool = ...,
    stacklevel: int = ...,
    extra: Mapping[str, object] | None = ...,
) -> None:
  ...

def debug(
    msg: object,
    *args: object,
    exc_info: _ExcInfo = ...,
    stack_info: bool = ...,
    stacklevel: int = ...,
    extra: Mapping[str, object] | None = ...,
) -> None:
  ...

def exception(
    msg: object,
    *args: object,
    exc_info: _ExcInfo = ...,
    stack_info: bool = ...,
    stacklevel: int = ...,
    extra: Mapping[str, object] | None = ...,
) -> None:
  ...

def log_every_n(
    level: int,
    msg: object,
    n: int,
    *args: object,
    use_call_stack: bool = ...,
    exc_info: _ExcInfo = ...,
    stack_info: bool = ...,
    stacklevel: int = ...,
    extra: Mapping[str, object] | None = ...,
) -> None:
  ...

def log_every_n_seconds(
    level: int,
    msg: object,
    n_seconds: float,
    *args: object,
    use_call_stack: bool = ...,
    exc_info: _ExcInfo = ...,
    stack_info: bool = ...,
    stacklevel: int = ...,
    extra: Mapping[str, object] | None = ...,
) -> None:
  ...

def log_first_n(
    level: int,
    msg: object,
    n: int,
    *args: object,
    use_call_stack: bool = ...,
    exc_info: _ExcInfo = ...,
    stack_info: bool = ...,
    stacklevel: int = ...,
    extra: Mapping[str, object] | None = ...,
) -> None:
  ...

def log_if(
    level: int,
    msg: object,
    condition: object,
    *args: object,
    exc_info: _ExcInfo = ...,
    stack_info: bool = ...,
    stacklevel: int = ...,
    extra: Mapping[str, object] | None = ...,
) -> None:
  ...

def log(
    level: int,
    msg: object,
    *args: object,
    exc_info: _ExcInfo = ...,
    stack_info: bool = ...,
    stacklevel: int = ...,
    extra: Mapping[str, object] | None = ...,
) -> None:
  ...

def vlog(
    level: int,
    msg: object,
    *args: object,
    exc_info: _ExcInfo = ...,
    stack_info: bool = ...,
    stacklevel: int = ...,
    extra: Mapping[str, object] | None = ...,
) -> None:
  ...

def vlog_is_on(level: int) -> bool:
  ...

def flush() -> None:
  ...

def level_debug() -> bool:
  ...

def level_info() -> bool:
  ...

def level_warning() -> bool:
  ...

level_warn = level_warning  # Deprecated function.

def level_error() -> bool:
  ...

def get_log_file_name(level: int = ...) -> str:
  ...

def find_log_dir_and_names(
    program_name: str | None = ..., log_dir: str | None = ...
) -> tuple[str, str, str]:
  ...

def find_log_dir(log_dir: str | None = ...) -> str:
  ...

def get_absl_log_prefix(record: logging.LogRecord) -> str:
  ...

_SkipLogT = TypeVar('_SkipLogT', str, Callable[..., Any])

def skip_log_prefix(func: _SkipLogT) -> _SkipLogT:
  ...

_StreamT = TypeVar('_StreamT')

class PythonHandler(logging.StreamHandler[_StreamT]):  # type: ignore[type-var]

  def __init__(
      self,
      stream: _StreamT | None = ...,
      formatter: logging.Formatter | None = ...,
  ) -> None:
    ...

  def start_logging_to_file(
      self, program_name: str | None = ..., log_dir: str | None = ...
  ) -> None:
    ...

  def use_absl_log_file(
      self, program_name: str | None = ..., log_dir: str | None = ...
  ) -> None:
    ...

  def _log_to_stderr(self, record: logging.LogRecord) -> None:
    ...

class ABSLHandler(logging.Handler):

  _current_handler: PythonHandler[Any]

  def __init__(self, python_logging_formatter: PythonFormatter) -> None:
    ...

  @property
  def python_handler(self) -> PythonHandler[Any]: ...
  def activate_python_handler(self) -> None:
    ...

  def use_absl_log_file(
      self, program_name: str | None = ..., log_dir: str | None = ...
  ) -> None:
    ...

  def start_logging_to_file(self, program_name=None, log_dir=None) -> None:
    ...

class PythonFormatter(logging.Formatter): ...

class ABSLLogger(logging.Logger):

  _frames_to_skip: set[tuple[str, str] | tuple[str, str, int]]

  @typing.override
  def fatal(
      self,
      msg: object,
      *args: object,
      exc_info: _ExcInfo = ...,
      stack_info: bool = ...,
      stacklevel: int = ...,
      extra: Mapping[str, object] | None = ...,
  ) -> NoReturn: ...
  @classmethod
  def register_frame_to_skip(
      cls, file_name: str, function_name: str, line_number: int | None = ...
  ) -> None:
    ...

# NOTE: Returns None before _initialize called but shouldn't occur after import.
def get_absl_logger() -> ABSLLogger:
  ...

# NOTE: Returns None before _initialize called but shouldn't occur after import.
def get_absl_handler() -> ABSLHandler:
  ...

def use_python_logging(quiet: bool = ...) -> None:
  ...

def use_absl_handler() -> None:
  ...

def _get_thread_id() -> int: ...
def _get_next_log_count_per_token(token: object) -> int: ...
