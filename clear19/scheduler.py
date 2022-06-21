import inspect
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from heapq import heappush, heappop
from math import floor
from queue import Queue, Full
from threading import Thread, Condition, Lock
from typing import Callable, Any, List, Dict

import psutil

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class TaskParameters:
    """Data object that the scheduler gives to the scheduled task."""
    command: Any
    """Data specified by the caller as the job was created."""
    scheduled_time: datetime
    """Time when this event should occur."""
    job_id: int
    """Id of the job."""
    job_run_count: int
    """The number of calls of this job."""


class Scheduler:
    """A non drifting scheduler for periodic events."""

    @dataclass(order=True)
    class _Job:
        next_run: datetime
        priority: float
        job_id: int
        start: datetime
        interval: timedelta
        task: Callable[[TaskParameters], None]
        command: Any
        run_count: int = 0
        stopped: bool = False

    _name: str
    _queue: List[_Job]
    _running: bool
    _queue_lock: Condition
    _thread: Thread
    _job_id: int = 0
    _job_id_lock: Lock
    _jobs: Dict[int, _Job]
    _jobs_lock: Lock

    def __init__(self, name: str = None):
        super().__init__()
        if name:
            self._name = f'Scheduler "{name}"'
        else:
            self._name = "Scheduler"
        self._running = True
        self._queue = []
        self._queue_lock = Condition()
        self._job_id_lock = Lock()
        self._jobs = dict()
        self._jobs_lock = Lock()
        self._thread = Thread(target=self._run)
        self._thread.name = self._name
        self._thread.start()

    def schedule_synchronous(self, interval: timedelta, task: Callable[[TaskParameters], Any],
                             command: Any = None, start: datetime = None, priority: float = 100):
        """
        Schedules a periodic event that will be called in the schedulers thread.
        :param interval: Time between two calls. If 0, the event will only occur once.
        :param task: Task to be called. Has to take one parameter of type TaskParameters.
        :param command: Arbitrary data that will be sent to the task within the TaskParameters object.
        :param start: First occurrence of the event. If None, it will be set to the next multiple time of interval.
        :param priority: When scheduled on the exact same time, the event with the lower priority will be called first.
        :return: Job id. The job can be stopped with this id.
        """
        assert len(inspect.signature(task).parameters) == 1, "Scheduler expects a callable that takes 1 argument."
        if start is None:
            start = datetime.fromtimestamp(floor(datetime.now().timestamp() / interval.total_seconds())
                                           * interval.total_seconds())
        with self._job_id_lock:
            self._job_id += 1
            job_id = self._job_id
            job = self._Job(start + interval, priority, job_id, start, interval, task, command)
        with self._jobs_lock:
            self._jobs[job_id] = job
        with self._queue_lock:
            heappush(self._queue, job)
            self._queue_lock.notify()
        return job_id

    def schedule_to_queue(self, interval: timedelta, queue: 'Queue[TaskParameters]',
                          command: Any = None, start: datetime = datetime.now(), priority: float = 100):
        """
        Schedules a periodic event that will send a TaskParameters object to given queue.
        :param interval: Task to be called. Has to take one parameter of type TaskParameters.
        :param queue: Thread save Queue which will receive the events.
        :param command: Arbitrary data that will be sent to the task within the TaskParameters object.
        :param start: First occurrence of the event. If None, it will be set to the next multiple time of interval.
        :param priority: When scheduled on the exact same time, the event with the lower priority will be called first.
        :return: Job id. The job can be stopped with this id.
        """
        return self.schedule_synchronous(interval, lambda p: self._put_to_queue(p, queue), command, start, priority)

    @staticmethod
    def _put_to_queue(task_parameters: TaskParameters, queue: 'Queue[TaskParameters]'):
        try:
            queue.put(task_parameters, block=False)
        except Full:
            pass

    def stop_job(self, job_id: int):
        """
        Stops the job with the given Id.
        :param job_id: Id of the job to stop. The is returned by the schedule_* functions and
                       on the TaskParameters object given in every job call.
        :return: If a job with the given id existed.
        """
        with self._jobs_lock:
            if job_id in self._jobs:
                self._jobs[job_id].stopped = True
                return True
            return False

    def stop_scheduler(self):
        """Stops the scheduler. No further tasks will be called."""
        with self._queue_lock:
            self.schedule_synchronous(timedelta(seconds=0), lambda i: self._stop(), priority=-float("inf"),
                                      start=datetime.now())

    def _stop(self):
        with self._queue_lock:
            self._running = False
            self._queue_lock.notify()

    def _run(self):
        log.debug(f"{self._name} started.")
        with self._queue_lock:
            while self._running:
                if self._queue:
                    job: Scheduler._Job = self._queue[0]
                    if job.next_run <= datetime.now():
                        heappop(self._queue)
                        if job.stopped:
                            with self._jobs_lock:
                                self._jobs.pop(job.job_id)
                        else:
                            job.run_count += 1
                            # noinspection PyBroadException
                            try:
                                job.task(TaskParameters(job.command, job.next_run, job.job_id, job.run_count))
                            except psutil.NoSuchProcess:
                                pass  # Sometimes it happens that a process is destroyed before we can read it's data.
                            except Exception as e:
                                log.exception(f'Failed to run job: {str(e)}')
                            if job.interval:
                                job.next_run = job.next_run + job.interval
                                heappush(self._queue, job)
                    if self._running:
                        self._queue_lock.wait((self._queue[0].next_run - datetime.now()).total_seconds())
                else:
                    self._queue_lock.wait()
        log.debug(f"{self._name} stopped.")
