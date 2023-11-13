import asyncio
import aiofiles
import os
import logging
import argparse

from aiohttp import web
from subprocess import PIPE


def get_args():
    parser = argparse.ArgumentParser(description='Скрипт скачивания фотографий')
    parser.add_argument(
        '--logging',
        nargs='?',
        type=bool,
        default=False,
        help='включить или выключить логирование'
    )
    parser.add_argument(
        '--delay',
        nargs='?',
        type=float,
        default=0.1,
        help='включить задержку ответа'
    )
    parser.add_argument(
        '--folder',
        nargs='?',
        type=str,
        default='photos',
        help='путь к каталогу с фотографиями'
    )
    parser.add_argument(
        '--size',
        nargs='?',
        type=int,
        default=102400,
        help='размер скачиваемого блока'
    )
    return parser.parse_args()


async def process_trminate(process):
    process.terminate()
    await process.communicate()
    return
    

async def archive(request):
    parser_args = get_args()
    photos_folder = parser_args.folder
    
    if parser_args.logging:
        logging.basicConfig(level=logging.INFO)
    
    archive_hash = request.match_info['archive_hash']
    
    if (not os.path.exists(f"./{photos_folder}/{archive_hash}")
            or not os.path.isdir(f"./{photos_folder}/{archive_hash}")):
        raise web.HTTPNotFound(
            text=f"<h2 style='color: red'>Архив {archive_hash} не существует или был удален</h2>",
            content_type='text/html')
    
    process = await asyncio.create_subprocess_exec(
        'zip',  '-r', '-', './', cwd=f"./{photos_folder}/{archive_hash}", stdout=PIPE, stderr=PIPE)
    await asyncio.sleep(parser_args.delay)
    chunk_number = 1
    logging.info(f'Get archive {photos_folder}/{archive_hash}')
    
    response = web.StreamResponse(status=200, reason='OK', headers={
            'Content-Type': 'multipart/x-mixed-replace',
            'CONTENT-DISPOSITION': 'attachment;filename="photos.zip"'})
    await response.prepare(request)
    
    try:
        chunk = await process.stdout.read(parser_args.size)
        while chunk:
            await asyncio.sleep(parser_args.delay)
            logging.info(f'Sending archive chunk {chunk_number}, {len(chunk)}')
            await response.write(chunk)
            chunk = await process.stdout.read(parser_args.size)
            chunk_number += 1
        
    except asyncio.CancelledError:
        logging.error(f'Download was interrupted.')
        await process_trminate(process)
        raise
    
    except IndexError:
        logging.error(f'Download IndexError')
        await process_trminate(process)
    
    except SystemExit:
        logging.error(f'Download SystemExit error')
        await process_trminate(process)
    
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
