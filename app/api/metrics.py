from fastapi import APIRouter
from fastapi.responses import Response
import psutil
import time
import os

metrics_router = APIRouter()

@metrics_router.get('/metrics')
async def get_metrics():
    """Endpoint Prometheus pour les métriques système"""
    
    # Métriques système
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Métriques applicatives
    process = psutil.Process(os.getpid())
    process_memory = process.memory_info()
    
    metrics = f"""# HELP zukii_python_cpu_percent CPU usage percentage
# TYPE zukii_python_cpu_percent gauge
zukii_python_cpu_percent {cpu_percent}

# HELP zukii_python_memory_percent Memory usage percentage
# TYPE zukii_python_memory_percent gauge
zukii_python_memory_percent {memory.percent}

# HELP zukii_python_disk_percent Disk usage percentage
# TYPE zukii_python_disk_percent gauge
zukii_python_disk_percent {disk.percent}

# HELP zukii_python_process_memory_rss Process RSS memory in bytes
# TYPE zukii_python_process_memory_rss gauge
zukii_python_process_memory_rss {process_memory.rss}

# HELP zukii_python_process_memory_vms Process VMS memory in bytes
# TYPE zukii_python_process_memory_vms gauge
zukii_python_process_memory_vms {process_memory.vms}

# HELP zukii_python_uptime_seconds Application uptime in seconds
# TYPE zukii_python_uptime_seconds gauge
zukii_python_uptime_seconds {time.time()}

# HELP zukii_python_info Application information
# TYPE zukii_python_info gauge
zukii_python_info{{version="1.0.0",name="zukii-python"}} 1
"""
    
    return Response(content=metrics, media_type='text/plain')
