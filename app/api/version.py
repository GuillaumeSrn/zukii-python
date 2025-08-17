from fastapi import APIRouter
from fastapi.responses import JSONResponse
import psutil
import time
import os

version_router = APIRouter()

@version_router.get('/version')
async def get_version():
    """Endpoint pour les informations de version"""
    return JSONResponse({
        "service": "zukii-python",
        "version": "1.0.0",
        "buildDate": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "uptime": time.time() - psutil.boot_time(),
        "pythonVersion": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
        "platform": os.sys.platform,
        "memory": {
            "total": psutil.virtual_memory().total,
            "available": psutil.virtual_memory().available,
            "percent": psutil.virtual_memory().percent
        }
    })
