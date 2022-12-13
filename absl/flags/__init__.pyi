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

from absl.flags import _argument_parser
from absl.flags import _defines
from absl.flags import _exceptions
from absl.flags import _flag
from absl.flags import _flagvalues
from absl.flags import _helpers
from absl.flags import _validators

# DEFINE functions. They are explained in more details in the module doc string.
# pylint: disable=invalid-name
DEFINE = _defines.DEFINE
DEFINE_flag = _defines.DEFINE_flag
DEFINE_string = _defines.DEFINE_string
DEFINE_boolean = _defines.DEFINE_boolean
DEFINE_bool = DEFINE_boolean  # Match C++ API.
DEFINE_float = _defines.DEFINE_float
DEFINE_integer = _defines.DEFINE_integer
DEFINE_enum = _defines.DEFINE_enum
DEFINE_enum_class = _defines.DEFINE_enum_class
DEFINE_list = _defines.DEFINE_list
DEFINE_spaceseplist = _defines.DEFINE_spaceseplist
DEFINE_multi = _defines.DEFINE_multi
DEFINE_multi_string = _defines.DEFINE_multi_string
DEFINE_multi_integer = _defines.DEFINE_multi_integer
DEFINE_multi_float = _defines.DEFINE_multi_float
DEFINE_multi_enum = _defines.DEFINE_multi_enum
DEFINE_multi_enum_class = _defines.DEFINE_multi_enum_class
DEFINE_alias = _defines.DEFINE_alias
# pylint: enable=invalid-name

# Flag validators.
register_validator = _validators.register_validator
validator = _validators.validator
register_multi_flags_validator = _validators.register_multi_flags_validator
multi_flags_validator = _validators.multi_flags_validator
mark_flag_as_required = _validators.mark_flag_as_required
mark_flags_as_required = _validators.mark_flags_as_required
mark_flags_as_mutual_exclusive = _validators.mark_flags_as_mutual_exclusive
mark_bool_flags_as_mutual_exclusive = _validators.mark_bool_flags_as_mutual_exclusive

# Flag modifiers.
set_default = _defines.set_default

# Key flag related functions.
declare_key_flag = _defines.declare_key_flag
adopt_module_key_flags = _defines.adopt_module_key_flags
disclaim_key_flags = _defines.disclaim_key_flags

# Module exceptions.
# pylint: disable=invalid-name
Error = _exceptions.Error
CantOpenFlagFileError = _exceptions.CantOpenFlagFileError
DuplicateFlagError = _exceptions.DuplicateFlagError
IllegalFlagValueError = _exceptions.IllegalFlagValueError
UnrecognizedFlagError = _exceptions.UnrecognizedFlagError
UnparsedFlagAccessError = _exceptions.UnparsedFlagAccessError
ValidationError = _exceptions.ValidationError
FlagNameConflictsWithMethodError = _exceptions.FlagNameConflictsWithMethodError

# Public classes.
Flag = _flag.Flag
BooleanFlag = _flag.BooleanFlag
EnumFlag = _flag.EnumFlag
EnumClassFlag = _flag.EnumClassFlag
MultiFlag = _flag.MultiFlag
MultiEnumClassFlag = _flag.MultiEnumClassFlag
FlagHolder = _flagvalues.FlagHolder
FlagValues = _flagvalues.FlagValues
ArgumentParser = _argument_parser.ArgumentParser
BooleanParser = _argument_parser.BooleanParser
EnumParser = _argument_parser.EnumParser
EnumClassParser = _argument_parser.EnumClassParser
ArgumentSerializer = _argument_parser.ArgumentSerializer
FloatParser = _argument_parser.FloatParser
IntegerParser = _argument_parser.IntegerParser
BaseListParser = _argument_parser.BaseListParser
ListParser = _argument_parser.ListParser
ListSerializer = _argument_parser.ListSerializer
CsvListSerializer = _argument_parser.CsvListSerializer
WhitespaceSeparatedListParser = _argument_parser.WhitespaceSeparatedListParser
EnumClassSerializer = _argument_parser.EnumClassSerializer
# pylint: enable=invalid-name

# Helper functions.
get_help_width = _helpers.get_help_width
text_wrap = _helpers.text_wrap
flag_dict_to_args = _helpers.flag_dict_to_args
doc_to_help = _helpers.doc_to_help

# The global FlagValues instance.
FLAGS = _flagvalues.FLAGS

