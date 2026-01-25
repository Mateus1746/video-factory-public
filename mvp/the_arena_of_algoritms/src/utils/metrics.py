import time
import logging
import os
import traceback
import numpy as np

# Configure logging to file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("debug_log.log", mode='w'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("Simulation")

class Telemetry:
    def __init__(self):
        self.start_time = time.time()
        self.frame_times = []
        self.update_times = []
        self.draw_times = []
        self.errors = []
        self.entity_stats = {}
        
    def log_error(self, msg, fatal=False):
        err_msg = f"{msg}\n{traceback.format_exc()}"
        if fatal:
            logger.critical(err_msg)
        else:
            logger.error(err_msg)
        self.errors.append({"time": time.time() - self.start_time, "msg": msg})

    def record_performance(self, update_ms, draw_ms, frame_ms):
        self.update_times.append(update_ms)
        self.draw_times.append(draw_ms)
        self.frame_times.append(frame_ms)
        
        # Keep only last 60 frames for average
        if len(self.frame_times) > 60:
            self.frame_times.pop(0)
            self.update_times.pop(0)
            self.draw_times.pop(0)

    def get_diagnostics(self):
        avg_fps = 1000.0 / np.mean(self.frame_times) if self.frame_times else 0
        avg_update = np.mean(self.update_times) if self.update_times else 0
        avg_draw = np.mean(self.draw_times) if self.draw_times else 0
        
        return {
            "fps": round(avg_fps, 2),
            "update_ms": round(avg_update, 2),
            "draw_ms": round(avg_draw, 2),
            "error_count": len(self.errors),
            "uptime": round(time.time() - self.start_time, 2)
        }

    def check_integrity(self, obj, name):
        """Checks for NaNs or Infinity in object attributes."""
        for attr, value in vars(obj).items():
            if isinstance(value, (float, int)):
                if np.isnan(value) or np.isinf(value):
                    self.log_error(f"INTEGRITY FAILURE: {name}.{attr} is {value}")
                    return False
            elif isinstance(value, (list, tuple)):
                # Optional deep check for lists
                pass
        return True

DIAGNOSTICS = Telemetry()
