from fastapi import FastAPI

app = FastAPI()

# Import and include routers
from .api.company_api import router as company_router
app.include_router(company_router, prefix='/company')
from .api.user_api import router as user_router
app.include_router(user_router, prefix='/user')
from .api.role_api import router as role_router
app.include_router(role_router, prefix='/role')
from .api.transcription_request_api import router as transcription_request_router
app.include_router(transcription_request_router, prefix='/transcription_request')
from .api.transcription_api import router as transcription_router
app.include_router(transcription_router, prefix='/transcription')
from .api.transcription_result_api import router as transcription_result_router
app.include_router(transcription_result_router, prefix='/transcription_result')
