import json
import os
import sys
import traceback

os.environ.setdefault("PYTHONIOENCODING", "utf-8")

from yolo_sam_features import extract_features


def main():
    try:
        payload = json.loads(sys.stdin.read())
        image_input = payload.get("image_input")
        sample_name = payload.get("sample_name")
        result = extract_features(image_input, sample_name=sample_name)
    except Exception as exc:
        traceback.print_exc(file=sys.stderr)
        result = {"error": str(exc)}

    print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
