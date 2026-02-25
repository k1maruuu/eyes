#Libraries
from fastapi import FastAPI, Request    
from fastapi.middleware.cors import CORSMiddleware

from src.api import main_router

from typing import Callable
import time

#Start
app = FastAPI()
app.include_router(main_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] #РАЗРЕШЕНИЕ НА ЗАПРОС С ЛЮБОГО САЙТА
) #ТОЧНОЕ СОВПАДЕНИЕ URL

@app.middleware("http")
async def my_middleware(request: Request, call_next: Callable):
    start = time.perf_counter()
    response = await call_next(request)
    end = time.perf_counter() - start

    ip_address = request.client.host
    response.headers["ip_address_cliend"] = ip_address
    response.headers["request_processing_time"] = f"{end}"

    return response


if __name__ == "__main__":
    import uvicorn 
    uvicorn.run("src.main:app", reload=True) #if Docker [host="0.0.0.0"]


