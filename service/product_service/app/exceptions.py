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


class ProductNotFoundError(AppError):
    pass


class CategoryNotFoundError(AppError):
    pass


class BrandNotFoundError(AppError):
    pass


class SlugAlreadyExistsError(AppError):
    pass
