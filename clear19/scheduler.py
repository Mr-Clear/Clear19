import inspect
import logging
import traceback
from dataclasses import dataclass
from datetime import datetime, timedelta
from heapq import heappush, heappop
from math import floor
from queue import Queue, Full
from threading import Thread, Condition, Lock
from typing import Callable, Any, List, Dict


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

    __name: str
    __queue: List[_Job] = []
    __running: bool
    __queue_lock: Condition = Condition()
    __thread: Thread
    __job_id: int = 0
    __job_id_lock: Lock = Lock()
    __jobs: Dict[int, _Job] = dict()
    __jobs_lock: Lock = Lock()

    def __init__(self, name: str = None):
        super().__init__()
        if name:
            self.__name = 'Scheduler "{}"'.format(name)
        else:
            self.__name = "Scheduler"
        self.__running = True
        self.__thread = Thread(target=self.__run)
        self.__thread.setName(self.__name)
        self.__thread.start()

    def schedule_synchronous(self, interval: timedelta, task: Callable[[TaskParameters], Any],
                             command: Any = None, start: datetime = None, priority: float = 100):
        """
        Schedules an periodic event that will be called in the schedulers thread.
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
        with self.__job_id_lock:
            self.__job_id += 1
            job_id = self.__job_id
            job = self._Job(start + interval, priority, job_id, start, interval, task, command)
        with self.__jobs_lock:
            self.__jobs[job_id] = job
        with self.__queue_lock:
            heappush(self.__queue, job)
            self.__queue_lock.notify()
        return job_id

    def schedule_to_queue(self, interval: timedelta, queue: 'Queue[TaskParameters]',
                          command: Any = None, start: datetime = datetime.now(), priority: float = 100):
        """
        Schedules an periodic event that will be send a TaskParameters object to given queue.
        :param interval: Task to be called. Has to take one parameter of type TaskParameters.
        :param queue: Thread save Queue which will receive the events.
        :param command: Arbitrary data that will be sent to the task within the TaskParameters object.
        :param start: First occurrence of the event. If None, it will be set to the next multiple time of interval.
        :param priority: When scheduled on the exact same time, the event with the lower priority will be called first.
        :return: Job id. The job can be stopped with this id.
        """
        return self.schedule_synchronous(interval, lambda p: self.__put_to_queue(p, queue), command, start, priority)

    @staticmethod
    def __put_to_queue(task_parameters: TaskParameters, queue: 'Queue[TaskParameters]'):
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
        with self.__jobs_lock:
            if job_id in self.__jobs:
                self.__jobs[job_id].stopped = True
                return True
            return False

    def stop_scheduler(self):
        """Stops the scheduler. No further tasks will be called."""
        with self.__queue_lock:
            self.schedule_synchronous(timedelta(seconds=0), lambda i: self.__stop(), priority=-float("inf"),
                                      start=datetime.now())

    def __stop(self):
        with self.__queue_lock:
            self.__running = False
            self.__queue_lock.notify()

    def __run(self):
        logging.debug("{} started.".format(self.__name))
        with self.__queue_lock:
            while self.__running:
                if self.__queue:
                    job: Scheduler._Job = self.__queue[0]
                    if job.next_run <= datetime.now():
                        heappop(self.__queue)
                        if job.stopped:
                            with self.__jobs_lock:
                                self.__jobs.pop(job.job_id)
                        else:
                            job.run_count += 1
                            # noinspection PyBroadException
                            try:
                                job.task(TaskParameters(job.command, job.next_run, job.job_id, job.run_count))
                            except Exception as e:
                                logging.info("Exception in scheduled job: {}".format(''.join(
                                    traceback.format_exception(None, e, e.__traceback__))))
                            if job.interval:
                                job.next_run = job.next_run + job.interval
                                heappush(self.__queue, job)
                    if self.__running:
                        self.__queue_lock.wait((self.__queue[0].next_run - datetime.now()).total_seconds())
                else:
                    self.__queue_lock.wait()
        logging.debug("{} stopped.".format(self.__name))
