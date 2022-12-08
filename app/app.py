from typing import Optional

from fastapi import FastAPI, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError

from app.databases import postgresql, clickhouse
from app.settings import settings
from app.databases.logger import start_log
from app.controllers import tools, auth
import sentry_sdk
import asyncio


def traces_sampler(context):
    path: Optional[str] = context.get('asgi_scope', {}).get('path')

    ignore_list = ['/', '/docs', '/health', '/metrics', '/openapi.json', '/documentation']

    if path in ignore_list or not path:
        return 0.0

    else:
        rate = 0.2 * settings.sentry_tracer_rate
        return rate if rate < 1.0 else 1.0


if settings.sentry_dsn:
    sentry_sdk.init(settings.sentry_dsn, traces_sampler=traces_sampler)


app = FastAPI(
    title="Then19 API",
    version="0.0.1",
)

app.include_router(tools.router, tags=["Tools"])
app.include_router(auth.router, tags=["Auth"])


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    if settings.sentry_dsn:
        sentry_sdk.set_context(
            f"422 validation error {settings.application_name}",
            {
                'url': request.url,
                'headers': request.headers,
                'exception_message': str(exc),
                'data': exc.body
            }
        )
        sentry_sdk.capture_message(f"{settings.application_name} {request.url.path} - 422 Validation Error")
        print('send to sentry')
    return await request_validation_exception_handler(request, exc)


@app.on_event("startup")
async def on_startup():
    asyncio.create_task(start_log())


@app.on_event("shutdown")
async def on_shutdown():
    await postgresql.close()
    await clickhouse.close()

