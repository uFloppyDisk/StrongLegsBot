"""
Copyright 2016 Pawel Bartusiak

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


class DCError(Exception):
    """Base class for exceptions in the default_commands package."""
    pass

# region General Exceptions


class DCSyntaxError(DCError):
    """Exception for syntax errors."""
    pass


class DCIncorrectAmountArgsError(DCError):
    """Exception for incorrect amount of arguments given."""
    pass


class DCIncorrectDataType(DCError):
    """Exception for incorrect datatype given."""
    pass


class DCUserlevelNoneError(DCError):
    """Exception for missing userlevel declaration."""
    pass


class DCUserlevelIncorrectError(DCError):
    """Exception for incorrect value for userlevel."""
    pass


class DCDatabaseEntryExists(DCError):
    """Exception for existing entry(s) matching new entry."""
    pass


class DCDatabaseEntryDoesNotExist(DCError):
    """Exception for missing database entries."""
    pass


class DCIntegerOutOfBounds(DCError):
    """Exception for integer out of set bounds."""
    pass

# endregion

# region Birthdays Exceptions


class DCBirthdaysFormatError(DCError):
    """Exception for incorrect format of birthdate submittion"""
    pass

# endregion
