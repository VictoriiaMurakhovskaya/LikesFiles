import os
import asyncio
import aiohttp
import json
import logging


async def getdata(client, name):
    req_body = 'http://147.78.65.148:3000/stat?v=' + name
    async with client.get(req_body) as response:
        try:
            assert response.status == 200
            respdata = await response.text(encoding='utf-8')
            data = json.loads(respdata)
            logging.info(name + ': ' + str(response.status) + '; ' + \
                         ' '.join([it + ':' + str(data[it]) for it in ['views', 'likes', 'dislikes']]))
            for item in ['views', 'likes', 'dislikes']:
                with open('output/' + name + '/' + item + '.txt', 'w') as f:
                    f.write(data[item])
            return name, respdata
        except:
            logging.error(name + ': ' + str(response.status))
            return name, None


async def mainloop(endings):
    loop = asyncio.get_running_loop()
    async with aiohttp.ClientSession(loop=loop) as client:
        task_list = [asyncio.create_task(getdata(client, item)) for item in endings]
        await asyncio.gather(*task_list)


def write_starter(endings):
    while True:
        asyncio.run(mainloop(endings))
