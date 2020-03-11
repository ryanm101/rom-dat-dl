#
# basedir = "/Commodore_Amiga/Retroplay/Commodore_Amiga_-_WHDLoad_-_Games"
# config_file = ""
#
# def getFDName(*args):
#     arr = args[0][32:].strip().split(' ')
#     if len(arr) > 1 and arr[len(arr)-1] != '':
#         args[1].append(arr[len(arr)-1])
#
# ftp.cwd(basedir)
#
# rawromdirs = []
#
# ftp.dir((lambda x: getFDName(x,rawromdirs)))
#
# romdirs = { i : [] for i in rawromdirs }
#
# for k in romdirs.keys():
#     ftp.cwd(basedir + '/' + k)
#     ftp.dir((lambda x: getFDName(x,romdirs[k])))
#     romdirs[k] = apply_filters(romdirs[k], filters)
#
#
# dl_list = gen_dl_paths(romdirs)
#
# ftp.quit()

import xml.etree.ElementTree as ET
import ftplib
import os

dat_path = "{}/Commodore Amiga - WHDLoad - Games (v2020-03-10).dat".format(base_path)
ftp_base = "/Commodore_Amiga/Retroplay"
filters = ["_AGA", "_CD32", "_CDTV", "_NTSC", "_Fr", "_De", "_Es", "_It", "_Pl"]

def apply_filters(arr, filters):
    for f in filters:
        arr = list(filter(lambda x: (f not in x), arr))
    return arr

def gen_paths(arr,basedir):
    flist = []
    for k in arr.keys():
        [ flist.append("{}/{}/{}".format(basedir,k,x)) for x in arr[k] ]
    return flist

tree = ET.parse(dat_path)
root = tree.getroot()

roms_top_dir = root.find('header').find('name').text.replace(' ','_')
ftp_path = "{}/{}".format(ftp_base,roms_top_dir)
outdir = "{}/{}".format(base_path,roms_top_dir)

romdirs = { i.attrib['name'] : list(map(lambda x: x.attrib['name'], i.findall('rom'))) for i in root.findall('machine') }

for k in romdirs.keys():
    romdirs[k] = apply_filters(romdirs[k],filters)

local_paths = gen_paths(romdirs,outdir)
failed_downloads = []

with ftplib.FTP(ftp_server, ftp_usr, ftp_pass) as ftp:
    totalfiles = len(local_paths)
    currentcount = 0
    for fn in local_paths:
        if not os.path.exists(fn):
            if not os.path.exists(os.path.dirname(fn)):
                os.mkdir(os.path.dirname(fn))
            print("Downloading {}: {}/{}".format(os.path.basename(fn),currentcount,totalfiles))
            with open(fn, 'wb') as f:
                try:
                    ftp.retrbinary('RETR ' + fn.replace(base_path,ftp_base), f.write)
                except:
                    print("Failed to download {}".format(os.path.basename(fn),currentcount,totalfiles))
                    failed_downloads.append(os.path.basename(fn))
                    f.close()
                    os.remove(fn)
        else:   
            print("{} already exists: {}/{}".format(os.path.basename(fn),currentcount,totalfiles))
        currentcount += 1

[ print("{} failed".format(i)) for i in failed_downloads]

ftp.quit()

