class AppError(Exception):
    pass


class DatabaseError(AppError):
    pass


class DuplicateEntryError(DatabaseError):
    pass


class InvalidTokenError(AppError):
    pass


class TokenExpiredError(AppError):
    pass


class UserProfileNotFoundError(AppError):
    pass


class AddressNotFoundError(AppError):
    pass


class AddressLimitExceededError(AppError):
    pass


class FavoriteAlreadyExistsError(AppError):
    pass


class FavoriteNotFoundError(AppError):
    pass
