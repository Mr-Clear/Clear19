from __future__ import annotations

import logging
import os
import urllib.request
from dataclasses import dataclass
from datetime import timedelta, datetime
from pathlib import Path
from queue import Queue
from threading import Thread, Lock
from typing import Dict, Callable, Optional
from urllib.parse import urlparse


def file_name_from_url(url: str) -> str:
    return os.path.basename(urlparse(url).path)


class DownloadManager:
    @dataclass
    class _DownloadJob:
        url: str
        callback: Callable[[bytes], None]

    @dataclass
    class _CacheEntry:
        content: bytes
        date: datetime

    _cache_path: Path
    _mem_cache: Dict[str, _CacheEntry]
    _mem_cache_lock: Lock
    _name_generator: Callable[[str], str]
    _download_queue: Queue[Optional[DownloadManager._DownloadJob]]
    _disk_load_queue: Queue[Optional[DownloadManager._DownloadJob]]
    _running: bool = True

    def __init__(self, cache_path: Path, name_generator: Callable[[str], str] = file_name_from_url):
        self._cache_path = cache_path
        self._name_generator = name_generator
        self._mem_cache = {}
        self._mem_cache_lock = Lock()
        self._download_queue = Queue()
        self._disk_load_queue = Queue()

        self.cache_path.mkdir(mode=0o755, parents=True, exist_ok=True)

        Thread(target=self._download_worker, name="DownloadManager download worker", daemon=True).start()
        Thread(target=self._disk_load_worker, name="DownloadManager disk load worker", daemon=True).start()

    def get(self, url: str, callback: Callable[[bytes], None], lifetime: timedelta = timedelta(days=30)) \
            -> Optional[bytes]:
        with self._mem_cache_lock:
            if url in self._mem_cache:
                if self._mem_cache[url].date + lifetime >= datetime.now():
                    return self._mem_cache[url].content
                else:
                    del self._mem_cache[url]

        cache_file = self.cache_path.joinpath(self.name_generator(url))
        if cache_file.exists():
            file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
            if file_time + lifetime >= datetime.now():
                self._disk_load_queue.put(self._DownloadJob(url, callback))
                return None
            else:
                logging.debug("File {} is too old. Deleting it.".format(cache_file))
                cache_file.unlink()

        self._download_queue.put(self._DownloadJob(url, callback))
        return None

    @property
    def cache_path(self) -> Path:
        return self._cache_path

    @property
    def name_generator(self) -> Callable[[str], str]:
        return self._name_generator

    @property
    def running(self) -> bool:
        return self._running

    def stop(self):
        self._running = False
        self._download_queue.put(None)

    def _download_worker(self):
        while self.running:
            job = self._download_queue.get()
            if not job:
                continue

            in_mem_cache = False
            with self._mem_cache_lock:
                if job.url in self._mem_cache:
                    job.callback(self._mem_cache[job.url].content)
                    in_mem_cache = True
            if not in_mem_cache:
                logging.debug("Downloading: {}".format(job.url))
                now = datetime.now()
                with urllib.request.urlopen(job.url) as file:
                    content = file.read()
                with self._mem_cache_lock:
                    self._mem_cache[job.url] = self._CacheEntry(content, now)
                cache_file = self.cache_path.joinpath(self.name_generator(job.url))
                with open(str(cache_file), "wb") as file:
                    file.write(content)
                if job.callback:
                    job.callback(content)

    def _disk_load_worker(self):
        while self.running:
            job = self._disk_load_queue.get()
            if not job:
                continue

            in_mem_cache = False
            with self._mem_cache_lock:
                if job.url in self._mem_cache:
                    job.callback(self._mem_cache[job.url].content)
                    in_mem_cache = True
            if not in_mem_cache:
                cache_file = self.cache_path.joinpath(self.name_generator(job.url))
                now = datetime.now()
                with open(str(cache_file), "rb") as file:
                    content = file.read()
                with self._mem_cache_lock:
                    self._mem_cache[job.url] = self._CacheEntry(content, now)
                if job.callback:
                    job.callback(content)
