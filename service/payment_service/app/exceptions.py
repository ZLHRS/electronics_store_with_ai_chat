class AppError(Exception):
    pass


class DatabaseError(AppError):
    pass


class InvalidTokenError(AppError):
    pass


class TokenExpiredError(AppError):
    pass


class PaymentNotFoundError(AppError):
    pass


class PaymentForbiddenError(AppError):
    pass


class PaymentAlreadyExistsError(AppError):
    pass


class InvalidPaymentStatusError(AppError):
    pass


class OrderNotFoundError(AppError):
    pass


class OrderForbiddenError(AppError):
    pass


class InvalidOrderStatusError(AppError):
    pass
