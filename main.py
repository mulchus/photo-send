from subprocess import PIPE
import asyncio


async def archive(delay, block_size):
    process = await asyncio.subprocess.create_subprocess_exec('zip', '-r', '-', '.', '-i', './photo/*', stdout=PIPE,
                                                              stderr=PIPE)
    x = 1
    while True:
        stdout = await process.stdout.read(block_size)
        # stderr = await process.stderr.read(block_size)
        print(x, len(stdout))   # , stderr.decode('utf-8'))
        x += 1
        # print(stderr.decode('utf-8'))
        with open('photo.zip', 'ab') as file:
            file.write(stdout)
        if process.stdout.at_eof():
            return
        await asyncio.sleep(delay)


async def main():
    task = asyncio.create_task(
        archive(1, 102400))
    await task
    

if __name__ == "__main__":
    asyncio.run(main())
