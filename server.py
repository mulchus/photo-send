import asyncio
import aiofiles

from aiohttp import web
from multidict import MultiDict
from subprocess import PIPE


UPLOADED_PART_SIZE = 102400


async def archive(request):
    archive_hash = request.match_info.get('archive_hash', "Anonymous")
    process = await asyncio.create_subprocess_shell(
        "zip -r - ./", cwd=f"./photo/{archive_hash}", stdout=PIPE, stderr=PIPE)
    all_archive = b''
    while True:
        stdout = await process.stdout.read(UPLOADED_PART_SIZE)
        all_archive += stdout
        
        if process.stdout.at_eof():
            headers = MultiDict({'Content-Disposition': 'Attachment; filename="photos.zip"'})
            return web.Response(headers=headers, body=all_archive)
        await asyncio.sleep(.1)
        

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
