from fcntl import ioctl
import os
import shlex
import time
from sys import argv
from subprocess import call, check_call
from multiprocessing import Process
from glob import glob
from asyncio import get_event_loop, sleep, ensure_future


defaultDrive='/dev/sr0'
storage = '/home/harpo/karaoke'

def detect(drive=defaultDrive):
    """detect_tray reads status of the CDROM_DRIVE.
    Statuses:
    1 = no disk in tray
    2 = tray open
    3 = reading tray
    4 = disk in tray
    """
    fd = os.open(drive, os.O_RDONLY | os.O_NONBLOCK)
    rv = ioctl(fd, 0x5326)
    os.close(fd)
    return rv

def rip(drive=defaultDrive, name=0):
    if detect(drive) is 4:
        # print(call(['sh', 'rip.sh', drive, str(name)]))
        directory = os.path.join(storage, str(name))
        call(['mkdir', directory])
        os.chdir(directory)
        check_call(shlex.split(f'cdrdao read-cd \
            --driver generic-mmc-raw \
            --device {drive} \
            --read-subchan rw_raw \
            --with-cddb \
            --eject \
            {str(name) + ".toc"}'))
        call(['eject', drive])

def convert(name=0):
    directory = os.path.join(storage, str(name))
    os.chdir(directory)
    check_call(shlex.split(f'python /home/harpo/cdgtools-0.3.2/cdgrip.py --with-cddb {str(name) + ".toc"}'))
    #call(['rm', 'data.bin'])

async def main():
    n = 1
    devices = glob('/dev/sr*')
    active = []
    processes = []
    while True:
        for d in set(devices) - set(active):
            status = detect(d)
            # print(f'{d} has status {status}')
            if status is 4:
                print(f'ripping! - {n} - {d}')
                active.append(d)
                processes.append((Process(target=rip, args=(d, n)), d, n))
                processes[-1][0].start()
                n += 1
        for p in processes:
            if not p[0].is_alive():
                print(f'{p} finished!')
                Process(target=convert, args=(p[2],)).start()
                active.remove(p[1])
                processes.remove(p)
        await sleep(1)

async def ripOne(drive, n):
    while True:
        if detect(drive) is 4:
            rip(argv[1], n)
            Process(target=convert, args=(n,)).start()
            n -= 1
        else:
            await sleep(1)


if __name__ =='__main__':
    loop = get_event_loop()
    if len(argv) > 1:
        # n = int(argv[2])
        ensure_future(ripOne(argv[1], int(argv[2])))
        loop.run_forever()

    else:
        ensure_future(main())
        loop.run_forever()
