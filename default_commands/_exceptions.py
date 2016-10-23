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


class DCUserlevelNoneError(DCError):
    """Exception for missing userlevel declaration."""
    pass


class DCUserlevelIncorrectError(DCError):
    """Exception for incorrect value for userlevel."""
    pass


class DCDatabaseEntryExists(DCError):
    """Exception for existing entry(s) matching new entry"""
    pass

# endregion

# region Birthdays Exceptions


class DCBirthdaysFormatError(DCError):
    """Exception for incorrect format of birthdate submittion"""
    pass

# endregion
