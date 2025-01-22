import aiohttp
import asyncio

async def test_proxy():
    url = "http://example.com"
    proxy = "http://aVD2fd:PKwhr7@134.195.153.156:9500"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, proxy=proxy) as resp:
            print(resp.status)
            print(await resp.text())

asyncio.run(test_proxy())
