class AppError(Exception):
    pass


class DatabaseError(AppError):
    pass


class InvalidTokenError(AppError):
    pass


class TokenExpiredError(AppError):
    pass


class SessionNotFoundError(AppError):
    pass


class SessionForbiddenError(AppError):
    pass


class IndexingError(AppError):
    pass
