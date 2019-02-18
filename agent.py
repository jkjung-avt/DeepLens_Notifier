"""agent.py
"""


import os
import sys
import logging
import logging as log

import cv2
from openvino.inference_engine import IENetwork, IEPlugin
from line_notify import send_message


LOG_FILE = os.environ['HOME'] + '/deeplens_agent.log'
MODEL = os.environ['HOME'] + \
        '/models/openvino/googlenet_fc_coco_SSD_300x300/FP16/deploy.xml'
DEVICE = 'GPU'
DETECT_CLASS = (1,)  # COCO class 1: 'person'
CONF_THRESHOLD = 0.2
VIDEO_IN = '/opt/awscam/out/ch2_out.mjpeg'
IMG_W = 640
IMG_H = 360
DO_IMSHOW = False
TMP_IMG = '/tmp/deeplens_agent.jpg'
LINE_TOKEN = os.environ['LINE_TOKEN']
EVENT_AVERAGE = 0.0
EVENT_TRIGGERED = True


def check_notify(detected, frame):
    """Check whether to send a notification based on detection status"""
    global EVENT_AVERAGE, EVENT_TRIGGERED
    EVENT_AVERAGE = EVENT_AVERAGE * 0.95 + float(detected) * 0.05
    if EVENT_AVERAGE >= 0.8 and not EVENT_TRIGGERED:
        log.info('Event triggered!')
        EVENT_TRIGGERED = True
        cv2.imwrite(TMP_IMG, frame)
        status = send_message(LINE_TOKEN,
                              'D5D01 meeting room is occupied.',
                              TMP_IMG)
        log.info('HTTP request status = {}'.format(status))
    if EVENT_AVERAGE < 0.2 and EVENT_TRIGGERED:
        log.info('Event relieved.')
        EVENT_TRIGGERED = False
        status = send_message(LINE_TOKEN,
                              'D5D01 meeting room is empty now...')
        log.info('HTTP request status = {}'.format(status))


def main():
    log.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(message)s',
                    filename=LOG_FILE)
    model_xml = MODEL
    model_bin = os.path.splitext(model_xml)[0] + '.bin'
    # Plugin initialization
    log.info('Initializing plugin for {} device...'.format(DEVICE))
    plugin = IEPlugin(device=DEVICE, plugin_dirs='')
    # Read IR
    log.info('Reading IR...')
    net = IENetwork(model=model_xml, weights=model_bin)

    assert plugin.device != 'CPU'
    assert len(net.inputs.keys()) == 1
    assert len(net.outputs) == 1

    input_blob = next(iter(net.inputs))
    out_blob = next(iter(net.outputs))
    log.info('Loading IR to the plugin...')
    exec_net = plugin.load(network=net, num_requests=2)
    # Read and pre-process input image
    n, c, h, w = net.inputs[input_blob].shape
    del net

    cap = cv2.VideoCapture(VIDEO_IN)
    cur_request_id = 0
    next_request_id = 1

    log.info("Starting inference in async mode...")
    log.info("To stop the demo execution press Esc button")
    initial_w = IMG_W
    initial_h = IMG_H
    ret, frame = cap.read()
    if not ret:
        sys.exit('No input frame!')
    frame = cv2.resize(frame, (IMG_W, IMG_H))
    while cap.isOpened():
        ret, next_frame = cap.read()
        if not ret:
            break
        next_frame = cv2.resize(next_frame, (IMG_W, IMG_H))
        # Main sync point:
        # in the Async mode we start the NEXT infer request, while
        # waiting for the CURRENT to complete
        in_frame = cv2.resize(next_frame, (w, h))
        in_frame = in_frame.transpose((2, 0, 1))  # HWC to CHW
        in_frame = in_frame.reshape((n, c, h, w))
        exec_net.start_async(request_id=next_request_id,
                             inputs={input_blob: in_frame})
        if exec_net.requests[cur_request_id].wait(-1) == 0:
            # Parse detection results of the current request
            res = exec_net.requests[cur_request_id].outputs[out_blob]
            event_detected = 0
            for obj in res[0][0]:
                if int(obj[1]) in DETECT_CLASS and obj[2] > CONF_THRESHOLD:
                    event_detected = 1
                    xmin = int(obj[3] * initial_w)
                    ymin = int(obj[4] * initial_h)
                    xmax = int(obj[5] * initial_w)
                    ymax = int(obj[6] * initial_h)
                    # Draw bounding box
                    color = (0, 255, 0)
                    cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)
            check_notify(event_detected, frame)
        if DO_IMSHOW:
            cv2.imshow("Detection Results", frame)
            if cv2.waitKey(1) == 27:
                break
        cur_request_id, next_request_id = next_request_id, cur_request_id
        frame = next_frame

    cv2.destroyAllWindows()
    del exec_net
    del plugin


if __name__ == '__main__':
    main()
