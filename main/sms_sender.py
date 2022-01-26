from datetime import datetime, timedelta
import json

import requests

def sendSmsOneContact(phone, message):
    dt = {
        "messages": [
            {
                "recipient": phone,
                "message-id": "abc000000001",
                "sms": {
                    "originator": "3700",
                    "content": {
                        "text": message
                    }
                }
            }
        ]
    }

    return requests.post(url="http://91.204.239.44/broker-api/send",
                           auth=('turoncompany', 'b7Z63C6siS'),
                           headers={'content-type': 'application/json'},
                           data=json.dumps(dt))
