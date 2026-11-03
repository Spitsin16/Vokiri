class AppError(Exception):
    status_code = 500


class ValidationError(AppError):
    status_code = 422


class NotFoundError(AppError):
    status_code = 404


class ConflictError(AppError):
    status_code = 409

class AuthenticationError(AppError):
    status_code = 401

class AiServiceError(AppError):
    status_code = 502

class RateLimitError(AppError):
    status_code = 429