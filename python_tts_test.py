#http://10.1.1.73:2020/dealAudio?text={{speakText}}&voice=yunyang&speed={{String((speakSpeed + 5) / 10 -1)}}
#speed:0-4.5

'''
原项目作者:https://github.com/lyz1810/edge-tts
'''
import logging
import os
import re
import sys
import uuid
from flask import Flask, request, make_response
from flask_cors import CORS
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

voiceMap = {
    "xiaoxiao": "zh-CN-XiaoxiaoNeural",
    "xiaoyi": "zh-CN-XiaoyiNeural",
    "yunjian": "zh-CN-YunjianNeural",
    "yunxi": "zh-CN-YunxiNeural",
    "yunxia": "zh-CN-YunxiaNeural",
    "yunyang": "zh-CN-YunyangNeural",
    "xiaobei": "zh-CN-liaoning-XiaobeiNeural",
    "xiaoni": "zh-CN-shaanxi-XiaoniNeural",
    "hiugaai": "zh-HK-HiuGaaiNeural",
    "hiumaan": "zh-HK-HiuMaanNeural",
    "wanlung": "zh-HK-WanLungNeural",
    "hsiaochen": "zh-TW-HsiaoChenNeural",
    "hsioayu": "zh-TW-HsiaoYuNeural",
    "yunjhe": "zh-TW-YunJheNeural",
    "Charline": "fr-BE-CharlineNeural",
    "Gerard": "fr-BE-GerardNeural",
}


# 根据传入的语音 ID，从 voiceMap 字典中获取对应的语音引擎名称
def getVoiceById(voiceId):
    return voiceMap.get(voiceId)

# 删除html标签
def remove_html(string):
    regex = re.compile(r'<[^>]+>')
    return regex.sub('', string)

# 将速度范围0-4.5转换为-50%到450%
def convert_speed_to_rate(speed):
    base_speed = 2.25  # 中间值，即0%对应的速度值
    rate = (speed - base_speed) * 100
    if rate < 0:
        rate = f"-{abs(rate)}%"
    else:
        rate = f"+{rate}%"
    return rate

# 删除10分钟前的语音文件
def delete_old_audio_files(directory):
    current_time = time.time()
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            file_age = current_time - os.path.getmtime(file_path)
            if file_age > 600:  # 10分钟 = 600秒
                os.remove(file_path)
                print(f"Deleted old audio file: {filename}")

# 创建音频文件
def createAudio(text, file_name, voiceId, speed):
    new_text = remove_html(text)
    print(f"Text without html tags: {new_text}")
    voice = getVoiceById(voiceId)
    if not voice:
        return "error params"

    pwdPath = os.getcwd()
    filePath = pwdPath + "/" + file_name
    dirPath = os.path.dirname(filePath)

    # 删除10分钟前的语音文件
    delete_old_audio_files(dirPath)

    if not os.path.exists(dirPath):
        os.makedirs(dirPath)
    if not os.path.exists(filePath):
        open(filePath, 'a').close()

    rate = convert_speed_to_rate(speed)
    script = f'edge-tts --voice {voice} --text "{new_text}" --rate {rate} --write-media {filePath}'
    os.system(script)
    return filePath  # 返回生成的音频文件路径

# 从请求参数中获取指定的参数值
def getParameter(paramName):
    if request.args.__contains__(paramName):
        return request.args[paramName]
    return ""

# 处理 /dealAudio 路径的请求
@app.route('/dealAudio', methods=['POST', 'GET'])
def dealAudio():
    text = getParameter('text')
    file_name = str(uuid.uuid4()) + ".mp3"
    voice = getParameter('voice')
    speed = float(getParameter('speed') or 2.25)  # 默认速度为2.25，即0%
    audio_file_path = createAudio(text, file_name, voice, speed)
    audio_url = request.host_url + 'static/' + file_name

    with open(audio_file_path, 'rb') as f:
        audio_data = f.read()

    response = make_response(audio_data)
    response.headers.set('Content-Type', 'audio/mpeg')
    response.headers.set('Content-Disposition', 'inline', filename='audio.mp3')

    return response

# 简单的首页路由
@app.route('/')
def index():
    return 'tts!'

if __name__ == "__main__":
    app.run(port=2020, host="127.0.0.1", debug=True)
