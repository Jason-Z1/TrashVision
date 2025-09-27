"""
Simple smoke-test script that POSTs a sample image to the local /predict endpoint and prints the response.
Usage:
python backend/scripts/test_predict.py path/to/test.jpg
"""
import sys
import requests


def main():
    if len(sys.argv) < 2:
        print('Usage: python backend/scripts/test_predict.py path/to/image.jpg')
        return
    path = sys.argv[1]
    url = 'http://127.0.0.1:8000/predict'
    with open(path, 'rb') as fh:
        files = {'file': fh}
        resp = requests.post(url, files=files)
        try:
            print(resp.status_code)
            print(resp.json())
        except Exception:
            print('Non-JSON response:')
            print(resp.text)

if __name__ == '__main__':
    main()
