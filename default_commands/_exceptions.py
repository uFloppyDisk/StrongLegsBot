class DCError(Exception):
    """Base class for exceptions in the default_commands package."""
    pass


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
