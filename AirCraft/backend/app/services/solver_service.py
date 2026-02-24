import logging
from concurrent.futures import ProcessPoolExecutor

solver_executor = ProcessPoolExecutor(max_workers=4)

logger = logging.getLogger("solver_service")
