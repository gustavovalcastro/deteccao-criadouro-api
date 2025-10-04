from fastapi import FastAPI        
from app.routers import routers   
from app.database import Base, engine  

Base.metadata.create_all(bind=engine) 

app = FastAPI(
    title="Breeding Site Detection API",      
    description="Integration API for Mosquito Breeding Sites Detection System", 
    version="1.0.0",
    docs_url="/swagger",   
    redoc_url=None                        
)

for router in routers:
    app.include_router(router)
