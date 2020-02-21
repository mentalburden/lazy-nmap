#!/bin/bash python3

import asyncio as asyncio

filepath = 'iplist.txt'
cmdToRun = 'nmap -F --open ' #needs a space at the end
iptargets = []
tasks = []

async def run(ip):
    cmd = cmdToRun + str(ip)
    outfilename = ip.rstrip("\n")+'-nmap-scan.txt'
    print(outfilename)
    nmapoutfile = open(outfilename, "a+")
    proc = await asyncio.create_subprocess_shell(cmd,stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    print(f'[{ip!r} exited with {proc.returncode}]')
    if stdout:
        nmapoutfile.write(stdout.decode())
        print(f'{stdout.decode()}')
    if stderr:
        nmapoutfile.write(stderr.decode())
        print(f'{stderr.decode()}')
    await asyncio.sleep(0.3)
    nmapoutfile.close()

async def loopmanager():
    for i in range(len(iptargets)):
        try:
            tasks.append(i)
            tasks[i] = loop.create_task(run(iptargets[i]))
        except IndexError:
            pass
    await asyncio.sleep(0.5)
    for i in range(len(tasks)):
        await tasks[i]

def readInFile(filepath):
    with open(filepath) as fp:
        line = fp.readline()
        jobnumber = 1
        while line:
                iptargets.append(line)
                #print("debug: - {}".format(line.strip()))
                line = fp.readline()
                jobnumber += 1

#main starts here
print("starting \'" + cmdToRun + "\' jobs for:")
if __name__ == '__main__':
    readInFile(filepath)
    loop = asyncio.get_event_loop()
    chonker = loop.run_until_complete(loopmanager())
