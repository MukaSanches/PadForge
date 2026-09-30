import compileall
import subprocess
import sys

ok = compileall.compile_dir("padforge", quiet=1)
if not ok:
    raise SystemExit("Compilation failed")
raise SystemExit(subprocess.call([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]))
