from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="DongHwa Backend API")

# CORS 설정 (Next.js 프론트엔드와 통신을 위한 설정)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js 개발 서버 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to DongHwa API"}

# 헬스 체크 엔드포인트
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# 나중에 다른 라우트를 추가할 수 있는 라우터
# from app.routes import your_router
# app.include_router(your_router)
