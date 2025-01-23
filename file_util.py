import asyncio
import aiofiles
import logging
from aiohttp import ClientSession

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

async def delay(seconds):
    await asyncio.sleep(seconds)

async def save_to_file(filename, data):
    try:
        async with aiofiles.open(filename, 'a', encoding='utf-8') as file:
            await file.write(f"{data}\n")
        log.info(f"Data saved to {filename}")
    except Exception as error:
        log.error(f"Failed to save data to {filename}: {error}")

async def save_to_file_fully(filename, data):
    try:
        async with aiofiles.open(filename, 'w', encoding='utf-8') as file:
            await file.write(data)
        log.info(f"Data saved to {filename}")
    except Exception as error:
        log.error(f"Failed to save data to {filename}: {error}")

async def read_file(path_file):
    try:
        async with aiofiles.open(path_file, 'r', encoding='utf-8') as file:
            contents = await file.read()
        data_lines = contents.split('\n')
        return [line.strip() for line in data_lines if line.strip()]
    except Exception as error:
        log.error(f"Error reading file: {error}")
        return []

def new_agent(proxy=None):
    if proxy:
        if proxy.startswith('http://'):
            connector = ProxyConnector.from_url(proxy)
        elif proxy.startswith('socks4://') or proxy.startswith('socks5://'):
            connector = ProxyConnector.from_url(proxy)
        else:
            log.warn(f"Unsupported proxy type: {proxy}")
            return None
        return ClientSession(connector=connector)
    return ClientSession()
