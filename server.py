import asyncio
import aiofiles
import os
import logging

from aiohttp import web
from subprocess import PIPE


logging.basicConfig(level=logging.DEBUG)

UPLOADED_PART_SIZE = 102400


async def archive(request):
    
    async def process_trminate():
        process.terminate()
        await process.communicate()
        return
    
    archive_hash = request.match_info.get('archive_hash', "Anonymous")
    
    if not os.path.exists(f"./photo/{archive_hash}") or not os.path.isdir(f"./photo/{archive_hash}"):
        raise web.HTTPNotFound(
            text=f"<h2 style='color: red'>Архив {archive_hash} не существует или был удален</h2>",
            content_type='text/html')
    
    process = await asyncio.create_subprocess_exec(
        'zip',  '-r', '-', './', cwd=f"./photo/{archive_hash}", stdout=PIPE, stderr=PIPE)
    await asyncio.sleep(.1)
    chunk_number = 1
    logging.info(f'Get archive {archive_hash}')
    
    response = web.StreamResponse(status=200, reason='OK', headers={
            'Content-Type': 'multipart/x-mixed-replace',
            'CONTENT-DISPOSITION': 'attachment;filename="photos.zip"'})
    await response.prepare(request)
    
    try:
        chunk = await process.stdout.read(UPLOADED_PART_SIZE)
        while chunk:
            await asyncio.sleep(.1)
            logging.info(f'Sending archive chunk {chunk_number}, {len(chunk)}')
            await response.write(chunk)
            chunk = await process.stdout.read(UPLOADED_PART_SIZE)
            chunk_number += 1
        
    except asyncio.CancelledError:
        logging.error(f'Download was interrupted.')
        await process_trminate()
    
    except IndexError:
        logging.error(f'Download IndexError')
        await process_trminate()
    
    except SystemExit:
        logging.error(f'Download SystemExit error')
        await process_trminate()
    
    return response


async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


if __name__ == '__main__':
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', archive),
    ])
    web.run_app(app)
