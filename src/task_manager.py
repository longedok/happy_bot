from __future__ import annotations

import asyncio
from asyncio import Semaphore, Task
from typing import Coroutine


class TaskManager:
    DEFAULT_MAX_PARALLEL_TASKS = 10

    def __init__(self, max_parallel_tasks: int = DEFAULT_MAX_PARALLEL_TASKS) -> None:
        self.max_parallel_tasks = max_parallel_tasks
        self.semaphore = Semaphore(self.max_parallel_tasks)
        self.tasks = set()

    def _on_task_done(self, task: Task) -> None:
        self.tasks.remove(task)
        self.semaphore.release()

    async def run_task(self, coro: Coroutine) -> None:
        await self.semaphore.acquire()
        task = asyncio.create_task(coro)
        self.tasks.add(task)
        task.add_done_callback(self._on_task_done)
