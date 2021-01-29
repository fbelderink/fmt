import os, stat
from pathlib import Path
from shutil import copyfile

bin_path = os.path.join(Path.home(), 'bin/')
Path(bin_path).mkdir(exist_ok=True)
copyfile('tool/fmt.py', bin_path + "fsmt")

st = os.stat(bin_path + "fsmt")
os.chmod(bin_path + "fsmt", st.st_mode | stat.S_IEXEC)

f = open(os.path.join(Path.home(), ".bash_profile"), "a")
f.write('export PATH=$PATH":$HOME/bin"')
f.close()

