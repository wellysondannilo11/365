import subprocess,sys
r=subprocess.run([sys.executable,'-m','ml.scripts.run_self_test'],capture_output=True,text=True)
print(r.stdout,end='');print(r.stderr,end='',file=sys.stderr);raise SystemExit(r.returncode)
