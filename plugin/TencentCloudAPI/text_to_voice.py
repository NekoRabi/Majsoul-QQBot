"""
:Author:  NekoRabi
:Create:  2023/6/16 2:18
:Update: /
:Describe: 语音转文本功能
:Version: 0.0.1
"""
import json
import base64
import time
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tts.v20190823 import tts_client, models

__all__ = ['VoiceCreater']


class VoiceCreater:

    def __init__(self, setting=None, secretId=None, secretKey=None, volume=1, speed=0.9, voicetype=1002, codec='mp3',
                 token=None, timestamp=None, **kwargs):
        self.secretId = secretId
        self.secretKey = secretKey
        if setting:
            self.volume = setting['volume']
            self.speed = setting['speed']
            self.voicetype = setting['voicetype']
            self.codec = setting['codec']
        else:
            self.token = token
            self.timestamp = timestamp
            self.volume = volume
            self.speed = speed
            self.voicetype = voicetype
            self.codec = codec

    def changesettings(self, key, value):
        if key == 'voicetype':
            self.voicetype = int(value)
        elif key == 'volume':
            self.volume = int(value)
        elif key == 'speed':
            self.speed = int(value)
        elif key == 'codec':
            self.codec = value

    def getbase64voice(self, text: str):
        try:
            cred = credential.Credential(
                secret_id=self.secretId, secret_key=self.secretKey)
            httpProfile = HttpProfile()
            httpProfile.endpoint = "tts.tencentcloudapi.com"

            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            client = tts_client.TtsClient(cred, "ap-shanghai", clientProfile)

            req = models.TextToVoiceRequest()
            params = {
                "Text": text,
                "SessionId": time.strftime('%Y/%m/%d/%H/%M', time.localtime(time.time())),
                "Volume": self.volume,
                "Speed": self.speed,
                "VoiceType": self.voicetype,
                "Codec": self.codec
            }
            req.from_json_string(json.dumps(params))

            resp = client.TextToVoice(req)
            jsstr = resp.to_json_string()
            audio = json.loads(jsstr)['Audio'].encode('utf-8')
            BytesToFile(f'./data/audio/{text}.{self.codec}', audio)
            return audio
        except TencentCloudSDKException as err:
            print(err)

    # 本地保存


def BytesToFile(filepath, bts):
    with open(filepath, 'wb') as v:
        f = base64.b64decode(bts)  # 进行解码
        v.write(f)
