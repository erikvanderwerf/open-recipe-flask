import asyncio
import logging
import os
import signal
from asyncio.tasks import shield
from pathlib import Path
from pprint import pprint
from typing import Coroutine, Callable

from openrecipeflask import indexer
from openrecipeflask.repo import Repository

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('orf')

SERVE_DIR = 'serve'
DB_PATH = Path(os.path.join(SERVE_DIR, 'db.sqlite'))
ORF_DIR = Path(os.path.join(SERVE_DIR, 'orf'))

LOOP = asyncio.get_event_loop()


def stop_loop():
    for task in asyncio.all_tasks():
        task.cancel()
    LOOP.close()


signal.signal(signal.SIGTERM, stop_loop)
if hasattr(signal, 'SIGKILL'):
    signal.signal(signal.SIGKILL, stop_loop)


async def schedule_periodic(name: str, delay: int, func: Callable[[], Coroutine]):
    max_consecutive_exceptions = 3
    current_consecutive_exceptions = 0
    try:
        while True:
            try:
                await shield(func())
                current_consecutive_exceptions = 0
            except asyncio.CancelledError:
                raise  # Don't mask Cancelled
            except Exception as e:
                current_consecutive_exceptions += 1
                logger.exception(f'An exception was raised during the execution of {name}')
                if current_consecutive_exceptions >= max_consecutive_exceptions:
                    logger.error(f'Killing {name} due to successive exceptions.')
                    raise
            await asyncio.sleep(delay)
    except asyncio.CancelledError:
        pass


tasks = asyncio.gather(
    schedule_periodic('IndexTask', 60, lambda: indexer.reindex(lambda: Repository(DB_PATH), ORF_DIR)),
    return_exceptions=True
)


try:
    LOOP.run_until_complete(tasks)
finally:
    LOOP.close()

print('Service Exiting. Collecting task results:')
pprint(tasks.result())