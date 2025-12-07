# Thread-safe pipe wrapper for inter-process communication
import multiprocessing as mp
import queue
import threading
import logging

logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Configure multiprocessing start method
try:
    if mp.get_start_method(allow_none=True) is None:
        mp.set_start_method("spawn")
except RuntimeError:
    logger.debug("Multiprocessing start method already configured")


class ParentPipe:
    """
    Thread-safe wrapper for pipe operations.
    All operations are funneled through a single worker thread to prevent race conditions.
    """
    def __init__(self, parent_synthesize_pipe, worker_join_timeout: float = 2.0):
        self.name = "ParentPipe"
        self._pipe = parent_synthesize_pipe
        self._closed = False
        self._request_queue = queue.Queue()
        self._stop_event = threading.Event()
        self._worker_join_timeout = worker_join_timeout
        self._worker_thread = threading.Thread(
            target=self._pipe_worker, name=f"{self.name}_Worker", daemon=True
        )
        self._worker_thread.start()

    def _pipe_worker(self):
        """Worker thread that processes all pipe operations sequentially."""
        while not self._stop_event.is_set():
            try:
                request = self._request_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            if request.get("type") == "CLOSE":
                result_queue = request.get("result_queue")
                if result_queue:
                    try:
                        result_queue.put(True, timeout=0.5)
                    except Exception:
                        pass
                break

            result_queue = request.get("result_queue")
            try:
                request_type = request["type"]
                
                if request_type == "SEND":
                    data = request["data"]
                    self._pipe.send(data)
                    if result_queue:
                        result_queue.put(None)
                        
                elif request_type == "RECV":
                    data = self._pipe.recv()
                    if result_queue:
                        result_queue.put(data)
                        
                elif request_type == "POLL":
                    timeout = request.get("timeout", 0.0)
                    result = self._pipe.poll(timeout)
                    if result_queue:
                        result_queue.put(result)
                else:
                    logger.debug(f"[{self.name}] Unknown request type: {request_type}")
                    if result_queue:
                        result_queue.put(None)
                        
            except (EOFError, BrokenPipeError, OSError) as error:
                logger.debug(f"[{self.name}] Pipe closed or error: {error}")
                if result_queue:
                    result_queue.put(error)
                break
            except Exception as error:
                logger.exception(f"[{self.name}] Unexpected error in worker")
                if result_queue:
                    result_queue.put(error)
                break

        try:
            self._pipe.close()
        except Exception as error:
            logger.debug(f"[{self.name}] Error closing pipe: {error}")
        logger.debug(f"[{self.name}] Worker thread exiting")

    def send(self, data, timeout: float = None):
        """Send data through the pipe."""
        if self._closed:
            raise RuntimeError("ParentPipe already closed")
        result_queue = queue.Queue()
        self._request_queue.put({"type": "SEND", "data": data, "result_queue": result_queue})
        try:
            return result_queue.get(timeout=timeout)
        except queue.Empty:
            raise TimeoutError("Send operation timed out")

    def recv(self, timeout: float = None):
        """Receive data from the pipe."""
        if self._closed:
            raise RuntimeError("ParentPipe already closed")
        result_queue = queue.Queue()
        self._request_queue.put({"type": "RECV", "result_queue": result_queue})
        try:
            data = result_queue.get(timeout=timeout)
            return data
        except queue.Empty:
            raise TimeoutError("Receive operation timed out")

    def poll(self, timeout: float = 0.0):
        """Check if data is available to receive."""
        if self._closed:
            return False
        result_queue = queue.Queue()
        self._request_queue.put({"type": "POLL", "timeout": timeout, "result_queue": result_queue})
        try:
            return result_queue.get(timeout=timeout + 0.1)
        except queue.Empty:
            return False

    def close(self):
        """Close the pipe and stop the worker thread."""
        if self._closed:
            return
        self._closed = True
        result_queue = queue.Queue()
        self._request_queue.put({"type": "CLOSE", "result_queue": result_queue})
        self._stop_event.set()
        self._worker_thread.join(timeout=self._worker_join_timeout)
        if self._worker_thread.is_alive():
            logger.warning(f"[{self.name}] Worker thread did not exit within timeout")


def SafePipe():
    """
    Create a pair of connected pipes for inter-process communication.
    Returns (parent_pipe, child_pipe) where parent_pipe is thread-safe.
    """
    parent_conn, child_conn = mp.Pipe()
    parent_pipe = ParentPipe(parent_conn)
    return parent_pipe, child_conn
