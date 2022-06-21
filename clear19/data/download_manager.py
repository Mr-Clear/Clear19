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
from urllib.error import URLError
from urllib.parse import urlparse

log = logging.getLogger(__name__)


def file_name_from_url(url: str) -> str:
    return os.path.basename(urlparse(url).path)


class DownloadManager:
    """
    Downloads files and caches them on disk and memory.
    """
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
        """
        :param cache_path: Path where cached files shall be stored.
        :param name_generator: Generates file names for the cached files from the URL. Default implementation just
                               preserves the file name.
        """
        self._cache_path = cache_path
        self._name_generator = name_generator
        self._mem_cache = {}
        self._mem_cache_lock = Lock()
        self._download_queue = Queue()
        self._disk_load_queue = Queue()

        self.cache_path.mkdir(mode=0o755, parents=True, exist_ok=True)

        Thread(target=self._download_worker, name="DownloadManager download worker", daemon=True).start()
        Thread(target=self._disk_load_worker, name="DownloadManager disk load worker", daemon=True).start()

    def get(self, url: str, callback: Callable[[bytes], None] = None, lifetime: timedelta = timedelta(days=30)) \
            -> Optional[bytes]:
        """
        Downloads a file. Content is only returned, if file is already in memory.
        :param url: URL of file.
        :param callback: Function that shall be called when the download is finished. Will instantly be called when
                         the file is in memory.
        :param lifetime: Maximum age of cached file.
        :return: Content of file or None.
        """
        with self._mem_cache_lock:
            if url in self._mem_cache:
                if self._mem_cache[url].date + lifetime >= datetime.now():
                    log.verbose(f"Getting URL '{url}' from memory cache.")
                    return self._mem_cache[url].content
                else:
                    del self._mem_cache[url]

        cache_file = self.cache_path.joinpath(self.name_generator(url))
        if cache_file.exists():
            file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
            if file_time + lifetime >= datetime.now():
                self._disk_load_queue.put(self._DownloadJob(url, callback))
                log.verbose(f"Loading URL '{url}' from file cache.")
                return None
            else:
                log.debug(f"File {cache_file} is too old. Deleting it.")
                cache_file.unlink()

        log.verbose(f"Downloading URL '{url}'.")
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
                    self._notify(job, self._mem_cache[job.url].content)
                    in_mem_cache = True
            if not in_mem_cache:
                log.debug(f"Downloading: {job.url}")
                now = datetime.now()
                try:
                    with urllib.request.urlopen(job.url) as file:
                        content = file.read()
                except URLError as err:
                    log.error(f'Failed to download "{job.url}".', exc_info=True)
                    content = None
                if content:
                    with self._mem_cache_lock:
                        self._mem_cache[job.url] = self._CacheEntry(content, now)
                    cache_file = self.cache_path.joinpath(self.name_generator(job.url))
                    with open(str(cache_file), 'wb') as file:
                        file.write(content)
                self._notify(job, content)

    def _disk_load_worker(self):
        while self.running:
            job = self._disk_load_queue.get()
            if not job:
                continue

            in_mem_cache = False
            with self._mem_cache_lock:
                if job.url in self._mem_cache:
                    self._notify(job, self._mem_cache[job.url].content)
                    in_mem_cache = True
            if not in_mem_cache:
                cache_file = self.cache_path.joinpath(self.name_generator(job.url))
                now = datetime.now()
                with open(str(cache_file), 'rb') as file:
                    content = file.read()
                with self._mem_cache_lock:
                    self._mem_cache[job.url] = self._CacheEntry(content, now)
                self._notify(job, content)

    @staticmethod
    def _notify(job: Optional[DownloadManager._DownloadJob], data: bytes):
        if job:
            try:
                job.callback(data)
            except Exception as e:
                log.error(f"Error when notify job: {e}", exc_info=True)
