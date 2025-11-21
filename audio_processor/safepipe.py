
# safepipe.py  -- improved safe pipe wrapper
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


try:
    if mp.get_start_method(allow_none=True) is None:
        mp.set_start_method("spawn")
except RuntimeError:
    logger.debug("multiprocessing start method already set")


class ParentPipe:
    """
    Thread-safe wrapper that funnels all pipe operations through a single worker thread.
    """
    def __init__(self, parent_synthesize_pipe, worker_join_timeout: float = 2.0):
        self.name = "ParentPipe"
        self._pipe = parent_synthesize_pipe
        self._closed = False
        self._request_queue = queue.Queue()
        self._stop_event = threading.Event()
        self._worker_thread = threading.Thread(
            target=self._pipe_worker, name=f"{self.name}_Worker", daemon=True
        )
        self._worker_thread.start()
        self._worker_join_timeout = worker_join_timeout

    def _pipe_worker(self):
        while not self._stop_event.is_set():
            try:
                request = self._request_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            if request.get("type") == "CLOSE":
                rq_res_q = request.get("result_queue")
                if rq_res_q:
                    try:
                        rq_res_q.put(True, timeout=0.5)
                    except Exception:
                        pass
                break

            result_queue = request.get("result_queue")
            try:
                if request["type"] == "SEND":
                    data = request["data"]
                    self._pipe.send(data)
                    if result_queue:
                        result_queue.put(None)
                elif request["type"] == "RECV":
                    data = self._pipe.recv()
                    if result_queue:
                        result_queue.put(data)
                elif request["type"] == "POLL":
                    timeout = request.get("timeout", 0.0)
                    res = self._pipe.poll(timeout)
                    if result_queue:
                        result_queue.put(res)
                else:
                    logger.debug("[%s] Unknown request type: %s", self.name, request.get("type"))
                    if result_queue:
                        result_queue.put(None)
            except (EOFError, BrokenPipeError, OSError) as e:
                logger.debug("[%s] Worker: pipe closed or error: %s", self.name, e)
                if result_queue:
                    result_queue.put(e)
                break
            except Exception as e:
                logger.exception("[%s] Worker: unexpected error", self.name)
                if result_queue:
                    result_queue.put(e)
                break

        try:
            self._pipe.close()
        except Exception as e:
            logger.debug("[%s] Worker: error closing pipe: %s", self.name, e)
        logger.debug("[%s] Worker exiting", self.name)

    def send(self, data, timeout: float = None):
        if self._closed:
            raise RuntimeError("ParentPipe already closed")
        result_queue = queue.Queue()
        self._request_queue.put({"type": "SEND", "data": data, "result_queue": result_queue})
        try:
            return result_queue.get(timeout=timeout)
        except queue.Empty:
            raise TimeoutError("Timed out waiting for send to complete")

    def recv(self, timeout: float = None):
        if self._closed:
            raise RuntimeError("ParentPipe already closed")
        result_queue = queue.Queue()
        self._request_queue.put({"type": "RECV", "result_queue": result_queue})
        try:
            data = result_queue.get(timeout=timeout)
            return data
        except queue.Empty:
            raise TimeoutError("Timed out waiting for recv")

    def poll(self, timeout: float = 0.0):
        if self._closed:
            return False
        result_queue = queue.Queue()
        self._request_queue.put({"type": "POLL", "timeout": timeout, "result_queue": result_queue})
        try:
            return result_queue.get(timeout=timeout + 0.1)
        except queue.Empty:
            return False

    def close(self):
        if self._closed:
            return
        self._closed = True
        result_queue = queue.Queue()
        self._request_queue.put({"type": "CLOSE", "result_queue": result_queue})
        self._stop_event.set()
        self._worker_thread.join(timeout=self._worker_join_timeout)
        if self._worker_thread.is_alive():
            logger.warning("[%s] Worker thread did not exit within timeout", self.name)


def SafePipe():
    """
    Creates a pair of connected pipes similar to mp.Pipe().
    Returns (parent_pipe, child_pipe) where parent_pipe is wrapped in ParentPipe.
    """
    parent_conn, child_conn = mp.Pipe()
    parent_pipe = ParentPipe(parent_conn)
    return parent_pipe, child_conn
