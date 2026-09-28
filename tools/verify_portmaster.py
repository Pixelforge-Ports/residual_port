from pathlib import Path
from verify_package import verify

if __name__ == "__main__":
    verify(Path(__file__).resolve().parents[1])
