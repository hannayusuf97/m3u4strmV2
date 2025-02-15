import uvicorn
from fastapi import FastAPI, Depends
from services.routes import router
from fastapi.middleware.cors import CORSMiddleware
from services.auth import router as jellyfin_auth
from services.auth import login_router as jellyfin_login_router
from services.auth import verify_jwt_token


app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the unprotected login router
app.include_router(jellyfin_login_router, prefix='/api/auth')

# Include the protected routes with authentication dependency
app.include_router(
    router,
    prefix='/api',
    dependencies=[Depends(verify_jwt_token)]
)

app.include_router(
    jellyfin_auth,
    prefix='/api/auth',
    dependencies=[Depends(verify_jwt_token)]
)

if __name__ == '__main__':
    uvicorn.run("main:app", host='0.0.0.0', port=8001, reload=False)
    
    
