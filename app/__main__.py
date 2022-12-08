import uvicorn

from app.app import app

uvicorn.run(app, port=8088)
