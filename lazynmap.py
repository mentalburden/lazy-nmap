#!/bin/bash python3

import asyncio as asyncio

iplistpath = 'iplist.txt'
outfilepath = '' #nothing or absolute path
liveHostsCmd = "nmap -sn ip/24 -oG - | awk '{ print $2 }'"
cmdToRun = 'nmap -T4 --min-parallelism 1 --max-parallelism 1 -F --open ' #needs a space at the end
iptargets = []
livetargets = []
livehosttasks = []
portscantasks = []


async def runlivehosts(ip):
    cmd = "nmap -sn " + str(ip.rstrip("\n")) + " -oG - | awk '/Up$/{print $2}'"
    proc = await asyncio.create_subprocess_shell(cmd,stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    if stdout:
        chonk = stdout.decode()
        for line in chonk.splitlines():
            livetargets.append(line)
    if stderr:
        print("very broken")
    await asyncio.sleep(0.3)


async def runportscan(ip):
    cmd = cmdToRun + str(ip.rstrip("\n"))
    outfilename = outfilepath+ip.rstrip("\n")+'-nmap-scan.txt'
    print(outfilename)
    nmapoutfile = open(outfilename, "a+")
    proc = await asyncio.create_subprocess_shell(cmd,stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
#    print(f'[{ip!r} exited with {proc.returncode}]')
    if stdout:
        nmapoutfile.write(stdout.decode())
#        print(f'{stdout.decode()}')
    if stderr:
        nmapoutfile.write(stderr.decode())
#        print(f'{stderr.decode()}')
    await asyncio.sleep(10)
    nmapoutfile.close()


async def livescanloopmanager():
    #start livehost scan to clean up actual target list and take care of cidrs
    for i in range(len(iptargets)):
        try:
            livehosttasks.append(i)
            livehosttasks[i] = loop.create_task(runlivehosts(iptargets[i]))
        except IndexError:
            pass
    await asyncio.sleep(0.5)
    for i in range(len(livehosttasks)):
        await livehosttasks[i]


async def portscanloopmanager():
    #start portscans for each livehost
    for i in range(len(livetargets)):
        try:
            portscantasks.append(i)
            portscantasks[i] = loop.create_task(runportscan(livetargets[i]))
        except IndexError:
            pass
    await asyncio.sleep(0.5)
    for i in range(len(portscantasks)):
        await portscantasks[i]


def readInFile(iplistpath):
    with open(iplistpath) as fp:
        line = fp.readline()
        jobnumber = 1
        while line:
                iptargets.append(line.rstrip("\n"))
                #print("debug: - {}".format(line.strip()))
                line = fp.readline()
                jobnumber += 1


#main starts here
if __name__ == '__main__':
    readInFile(iplistpath)
    loop = asyncio.get_event_loop()
    chonker = loop.run_until_complete(livescanloopmanager())
    chonker2 = loop.run_until_complete(portscanloopmanager())
