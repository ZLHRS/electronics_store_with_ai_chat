class AppError(Exception):
    pass


class DatabaseError(AppError):
    pass


class DuplicateEntryError(DatabaseError):
    pass


class UserAlreadyExistsError(AppError):
    pass


class InvalidCredentialsError(AppError):
    pass


class InvalidTokenError(AppError):
    pass


class TokenExpiredError(AppError):
    pass


class TokenReuseError(AppError):
    pass


class AlreadyLoggedInError(AppError):
    pass
