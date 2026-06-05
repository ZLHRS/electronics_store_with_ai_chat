class AppError(Exception):
    pass


class DatabaseError(AppError):
    pass


class InvalidTokenError(AppError):
    pass


class TokenExpiredError(AppError):
    pass


class CartNotFoundError(AppError):
    pass


class CartItemNotFoundError(AppError):
    pass


class ProductNotFoundError(AppError):
    pass


class ProductNotAvailableError(AppError):
    pass


class InvalidQuantityError(AppError):
    pass
