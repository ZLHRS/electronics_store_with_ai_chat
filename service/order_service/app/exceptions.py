class AppError(Exception):
    pass


class DatabaseError(AppError):
    pass


class InvalidTokenError(AppError):
    pass


class TokenExpiredError(AppError):
    pass


class OrderNotFoundError(AppError):
    pass


class OrderAccessDeniedError(AppError):
    pass


class OrderCancelForbiddenError(AppError):
    pass


class CartEmptyError(AppError):
    pass


class ProductNotFoundError(AppError):
    pass


class ProductNotAvailableError(AppError):
    pass
