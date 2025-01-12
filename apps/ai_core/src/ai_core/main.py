from fastapi import FastAPI

app = FastAPI()

# Import and include routers
from .api.config_api import router as config_router
app.include_router(config_router, prefix='/v1', tags=["Config"])
from .api.company_api import router as company_router
app.include_router(company_router, prefix='/v1', tags=["Company"])
from .api.user_api import router as user_router
app.include_router(user_router, prefix='/v1', tags=["User"])
from .api.role_api import router as role_router
app.include_router(role_router, prefix='/v1', tags=["Role"])
from .api.transcription_request_api import router as transcription_request_router
app.include_router(transcription_request_router, prefix='/v1', tags=["Transcription Request"])
from .api.transcription_api import router as transcription_router
app.include_router(transcription_router, prefix='/v1', tags=["Transcription"])
from .api.transcription_result_api import router as transcription_result_router
app.include_router(transcription_result_router, prefix='/v1', tags=["Transcription Result"])
