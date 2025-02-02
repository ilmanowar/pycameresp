""" Patch the initsetup.py """
# pylint:disable=consider-using-f-string
# pylint:disable=unspecified-encoding
from zlib import *
from binascii import *

filesToAdd = [
	("","modules/main.py"),
	("","modules/pycameresp.py"),
]

if __name__ == "__main__":
	from sys import argv
	if len(argv) > 1:
		root = argv[1]
	else:
		root = "firmware"

	fileSetup='''
    print("Install %(filename)s")
    with open("%(filename)s", "w") as f:
        f.write(decompress(a2b_base64(%(content)s)))
'''
	from os.path import split
	patchIni=""
	import glob
	for filename in glob.glob("modules/www/*.css"):
		filesToAdd.append(("www",filename))
	for filename in glob.glob("modules/www/*.js"):
		filesToAdd.append(("www",filename))
	for path, filename in filesToAdd:
		content = b2a_base64(compress(open(filename,"rb").read()))
		if path != "":
			patchIni += "    try:\n        uos.mkdir('%s')\n    except: pass\n"%path
			filename = "%s/%s"%(path, split(filename)[1])
		else:
			filename = split(filename)[1]
		patchIni += fileSetup%locals()

	inisetup = open("patch/python/micropython/ports/esp32/modules/inisetup.py","r").read()
	open(root + "/micropython/ports/esp32/modules/inisetup.py","w").write(inisetup%patchIni)
	inisetup = open("patch/python/micropython/ports/rp2/modules/_boot.py","r").read()
	open(root + "/micropython/ports/rp2/modules/_boot.py","w").write(inisetup%patchIni)
	import time
	year,month,day,hour,minute,second,weekday,yearday = time.localtime()[:8]
	open("modules/lib/tools/builddate.py","w").write("''' Build date '''\ndate=b'%04d/%02d/%02d  %02d:%02d:%02d'\n"%(year,month,day,hour,minute,second))
