import json
import requests
from flask import Flask
from flask import request
import arrow


app = Flask(__name__)


@app.route('/webhook', methods=['POST', 'GET'])
def send():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
    }
    if request.method == 'POST':
        post_data = request.get_data()
        # https://oapi.dingtalk.com/robot/send?access_token=00e32d52eb765ca41ebeac5661c356c3fe95e3092bf4d2637df0a7caa9eeac5c
        send_alert(bytes2json(post_data), "00e32d52eb765ca41ebeac5661c356c3fe95e3092bf4d2637df0a7caa9eeac5c", headers)
        return 'success'
    else:
        return 'weclome to use prometheus alertmanager dingtalk webhook server!'


def bytes2json(data_bytes):
    data = data_bytes.decode('utf8').replace("'", '"')
    return json.loads(data)


def send_alert(data, token, headers):

    url = 'https://oapi.dingtalk.com/robot/send?access_token=%s' % token
    print(data['alerts'])
    for output in data['alerts'][:]:
        # 恢复模板
        if output['status'] == 'resolved':
            send_data = {
                "msgtype": "markdown",
                "markdown": {
                    # 关键词设置
                    "title": "black",
                    "text": "## 恢复主题: %s \n" % output['labels']['alertname'] +
                            "**恢复时间**: %s \n\n" %
                            arrow.get(output['endsAt']).to('Asia/Shanghai').format('YYYY-MM-DD HH:mm:ss ZZ').split(
                                '+')[
                                0] +
                            "**恢复级别**: %s \n\n" % output['status'] +
                            "**恢复实例**: %s \n\n" % output['labels']['instance'].split(':')[0] +
                            "**恢复详情**: {}{} \n\n".format(output['labels']['alertname'], "恢复正常") +
                            "**恢复详情内容**: {}{}{} \n\n".format(output['labels']['instance'].split(':')[0], output['labels']['nodename'], output['annotations']['description']).replace("大于", "")
                }
            }
        # 报警模板
        else:
            send_data = {
                "msgtype": "markdown",
                "markdown": {
                    # 关键词设置
                    "title": "black",
                    "text": "## 告警主题: %s \n" % output['labels']['alertname'] +
                            "**触发时间**: %s \n\n" %
                            arrow.get(output['startsAt']).to('Asia/Shanghai').format('YYYY-MM-DD HH:mm:ss ZZ').split('+')[
                                0] +
                            "**告警级别**: %s \n\n" % output['status'] +
                            "**告警实例**: %s \n\n" % output['labels']['instance'].split(':')[0] +
                            "**告警详情**: %s \n\n" % output['annotations']['summary'] +
                            "**告警详情内容**: {}{}{} \n\n".format(output['labels']['instance'].split(':')[0], output['labels']['nodename'], output['annotations']['description'])
                }
            }
        req = requests.post(url, headers=headers, json=send_data)
        result = req.json()
        if result['errcode'] != 0:
            print('notify dingtalk error: %s' % result['errcode'])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
