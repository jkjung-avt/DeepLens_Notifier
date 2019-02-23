# DeepLens_Notifier

An AWS DeepLens agent which sends a LINE Notify message to me whenever it detects an event.

I'm using Intel OpenVINO Toolkit to speed up CNN inferencing on the AWS DeepLens.

To test the script, check out the code to ${HOME}/project/DeepLens_Notifier and do the following:

```shell
$ cd ${HOME}/project
$ git clone https://github.com/jkjung-avt/DeepLens_Notifier.git
# Set your LINE_TOKEN in setvars.sh
# For example, setvars.sh contains a line of 'export LINE_TOKEN=xxxxxx'
$ source setvars.sh
$ python3 agent.py
```

To let the agent start automatically (at each system reboot),

```shell
$ sudo cp deeplens-notify.service /etc/systemd/system
$ sudo systemctl daemon-reload
$ sudo systemctl enable deeplens-notify.service
# The service would start when the system is rebooted afterwards
```
