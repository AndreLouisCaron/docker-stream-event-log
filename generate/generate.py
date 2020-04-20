# -*- coding: utf-8 -*-


import asyncio
import itertools
import json
import logging
import os
import signal

from contextlib import (
    asynccontextmanager,
    contextmanager,
    closing,
    ExitStack,
)
from datetime import timedelta
from pathlib import Path


logger = logging.getLogger(__name__)


@asynccontextmanager
async def background_task(coro, loop=None):
    """Run a task in the background (and prevent leaking it)."""

    loop = loop or asyncio.get_event_loop()

    task = loop.create_task(coro)
    try:
        yield task
    finally:
        task.cancel()
        await asyncio.wait({task})


@asynccontextmanager
async def background_stream(path, loop=None):
    """Write to a file in the background (via a ``asyncio.Queue``)."""

    loop = loop or asyncio.get_event_loop()
    queue = asyncio.Queue(loop=loop)

    async def consume():
        while True:
            print('[stream] open "%s"!' % (
                path,
            ))
            with open(path, 'wb') as stream:
                while True:
                    try:
                        data = await queue.get()
                        if data is None:
                            break
                        print('[stream] write (%d bytes)!' % (
                            len(data),
                        ))
                        # NOTE: shield the executor task from cancellation to
                        #   ensure `stream.write()` completes before we close
                        #   the file.
                        await asyncio.shield(
                            loop.run_in_executor(None, stream.write, data)
                        )
                    except asyncio.CancelledError:
                        print('[stream] cancelled!')
                        raise
                    except Exception:
                        logger.exception('in stream')

    async with background_task(consume()):
        yield queue


@contextmanager
def signal_handler(loop, signum, callback, *args):
    """Subscribe/unsubscribe to a POSIX signal."""

    loop.add_signal_handler(signum, callback, *args)
    try:
        yield
    finally:
        loop.remove_signal_handler(signum)


async def main(loop=None):
    """Continuously emit JSON logs (compatible with ``logrotate``)."""

    loop = loop or asyncio.get_event_loop()

    interval = timedelta(seconds=1)

    pid_path = Path(os.environ['PID_PATH'])
    log_path = Path(os.environ['LOG_PATH'])

    # Write a PID file so `logrotate` can find us.
    pid_path.write_text('%d' % (
        os.getpid(),
    ))

    # Stream data to a log file (and reopen on SIGHUP).
    try:
        async with background_stream(log_path, loop=loop) as q:
            with signal_handler(loop, signal.SIGHUP, q.put_nowait, None):
                for i in itertools.count():
                    data = json.dumps({
                        'i': i,
                    })
                    q.put_nowait(data.encode('utf-8') + b'\n')
                    await asyncio.sleep(interval.total_seconds())
    except asyncio.CancelledError:
        pass
    except Exception:
        logger.exception('in main')

    # Done!
    print('[main] done!')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    with closing(loop):
        task = loop.create_task(main())
        try:
            loop.run_until_complete(task)
        except KeyboardInterrupt:
            while not task.done():
                task.cancel()
                loop.run_until_complete(task)
