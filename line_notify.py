"""test.py

A simple script for testing how to send a LINE Notify message or image

Reference: https://engineering.linecorp.com/zh-hant/blog/using-line-notify-to-send-stickers-and-upload-images/
"""

import os
import sys
import argparse
import requests


URL = 'https://notify-api.line.me/api/notify'


def send_message(token, msg, img=''):
    """Send a LINE Notify message (with or without an image)"""
    headers = {'Authorization': 'Bearer ' + token}
    payload = {'message': msg}
    if img:
        file = {'imageFile': open(img, 'rb')}
        r = requests.post(URL, headers=headers, params=payload, files=file)
    else:
        r = requests.post(URL, headers=headers, params=payload)
    return r.status_code


def main():
    try:
        token = os.environ['LINE_TOKEN']
    except KeyError:
        sys.exit('LINE_TOKEN is not defined!')
    parser = argparse.ArgumentParser(
        description='Send a LINE Notify message, possibly with an image.')
    parser.add_argument('--img_file', help='the image file to be sent')
    parser.add_argument('message')
    args = parser.parse_args()
    status_code = send_message(token, args.message, args.img_file)
    print('status_code = {}'.format(status_code))


if __name__ == '__main__':
    main()