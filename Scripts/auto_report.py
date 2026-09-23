import sys
import time
from pathlib import Path
import subprocess
from datetime import datetime

RUN_EVERY = 5
CYCLES = 5


ROOT_DIR = Path(__file__).resolve().parent
REPORTS_SCRIPT = ROOT_DIR / "reports.py"
OUT_DIR = ROOT_DIR / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)


AUDIT_LOG = OUT_DIR / "audit.log"


def log(msg):
    line = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {msg}\n"

    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(line)


def main():
    print("AUTO REPORT START")
    print("Script reports.py:", REPORTS_SCRIPT)
    print("Director outputs:", OUT_DIR)

    for i in range(1, CYCLES + 1):
        log(f"Cycle: {i} started")

        res = subprocess.run(
            [sys.executable, str(REPORTS_SCRIPT)],
            cwd=str(ROOT_DIR),
            capture_output=True,
            text=True
        )

        print(f"\n=== Cycle {i} ===")
        if res.stdout:
            print(res.stdout)
        if res.stderr:
            print("STDERR:", res.stderr)

        if res.returncode != 0:
            log(f"Cycle {i} failed (code={res.returncode})")
            break
        else:
            log(f"Cycle {i} passed")


        if i < CYCLES:
            time.sleep(RUN_EVERY)

    print("AUTO REPORT END")


if __name__ == "__main__":
    main()