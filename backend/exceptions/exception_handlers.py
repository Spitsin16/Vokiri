from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.exceptions.exceptions_classes import AppError


async def handle_app_error(request: Request,error: AppError,) -> JSONResponse:
    return JSONResponse(
        status_code=error.status_code,
        content={"detail": str(error)},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        AppError,
        handle_app_error,
    )
