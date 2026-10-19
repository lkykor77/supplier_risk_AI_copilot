"""Download OCR language data once; supplier documents are never uploaded."""

from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parent


def main():
    folder = ROOT / ".cache/ocr-languages"
    folder.mkdir(parents=True, exist_ok=True)
    for language in ["eng", "kor"]:
        target = folder / (language + ".traineddata.gz")
        if target.exists():
            print(language + " language data is already present.")
            continue
        print("Downloading " + language + " OCR language data…", flush=True)
        request = urllib.request.Request("https://tessdata.projectnaptha.com/4.0.0/" + language + ".traineddata.gz")
        with urllib.request.urlopen(request, timeout=60) as response:
            data = response.read(60000000)
        if not data.startswith(b"\x1f\x8b"):
            raise ValueError("Language download was not the expected compressed data.")
        target.write_bytes(data)
    print("Local English/Korean OCR data is ready. No supplier files were transmitted.")


if __name__ == "__main__":
    main()
