import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENV_PY = ROOT / "venv" / "bin" / "python3"


def run_extraction():
    cmd = [str(VENV_PY), str(ROOT / "extraction" / "stripe_extractor.py")]
    print("Running extraction:", " ".join(cmd))
    proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
    print(proc.stdout)


def run_transformation():
    cmd = [str(VENV_PY), str(ROOT / "transformation" / "transform_stripe.py")]
    print("Running transformation:", " ".join(cmd))
    proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
    print(proc.stdout)


def run_loader():
    cmd = [str(VENV_PY), str(ROOT / "loading" / "load_to_sql.py")]
    print("Running loader:", " ".join(cmd))
    proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
    print(proc.stdout)


def main():
    try:
        run_extraction()
        run_transformation()
        run_loader()
        print("Pipeline finished successfully")
    except subprocess.CalledProcessError as e:
        print("Pipeline failed:")
        print(e.stdout)
        print(e.stderr)
        sys.exit(e.returncode)


if __name__ == "__main__":
    main()