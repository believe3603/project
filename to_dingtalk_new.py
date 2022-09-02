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
        send_alert(bytes2json(post_data), "token", headers)
        return 'success'
    else:
        return 'weclome to use prometheus alertmanager dingtalk webhook server!'


def bytes2json(data_bytes):
    data = data_bytes.decode('utf8').replace("'", '"')
    return json.loads(data)


def alert_data(out, nodename, name, flag):

    # 判断是否是mq报警(1:不是mq报警，0：是mq报警)
    if flag == 1:
        # 判断是恢复时间还是报警时间
        if name == "告警":
            t1 = 'startsAt'
            details = "**{}详情**: {} \n\n".format(name, out['annotations']['summary'])
            details_content = "**{}详情内容**: {}{}{} \n\n".format(name, out['labels']['instance'].split(':')[0], nodename, out['annotations']['description'])
            instance = "**{}实例**: {} \n\n".format(name, out['labels']['instance'].split(':')[0])
        else:
            # 恢复
            t1 = 'endsAt'
            details = "**{}详情**: {}{} \n\n".format(name, out['labels']['alertname'], "恢复正常")
            details_content = "**{}详情内容**: {}{}{} \n\n".format(name, out['labels']['instance'].split(':')[0], nodename, out['annotations']['description']).replace("大于", "")
            instance = "**{}实例**: {} \n\n".format(name, out['labels']['instance'].split(':')[0])

    else:
        if name == "告警":
            t1 = 'startsAt'
            instance = '\b'
            details = "**{}详情**: {} \n\n".format(name, out['annotations']['summary'])
            details_content = "**{}详情内容**: {} \n\n".format(name, out['annotations']['description'])
        else:
            t1 = 'endsAt'
            instance = '\b'
            details = "**{}详情**: {} \n\n".format(name, out['annotations']['summary'])
            details_content = "**{}详情内容**: {} \n\n".format(name, out['annotations']['description'])

    data = {
        "msgtype": "markdown",
        "markdown": {
            # 关键词设置
            # "title": "black",
            "title": "test",
            "text": "## {}主题: {} \n".format(name, out['labels']['alertname']) +
                    "**{}时间**: {} \n\n".format(name, arrow.get(out[t1]).to('Asia/Shanghai').format('YYYY-MM-DD HH:mm:ss ZZ').split(
                        '+')[0])
                    +
                    "**{}级别**: {} \n\n".format(name, out['status']) +
                    instance +
                    details +
                    details_content
        }
    }
    return data


def send_alert(data, token, headers):

    url = 'https://oapi.dingtalk.com/robot/send?access_token=%s' % token
    print(data['alerts'])
    for output in data['alerts'][:]:
        try:
            # 没有nodename 字段就置空，有就赋值
            if output['labels']['nodename'] != "":
                nodename = output['labels']['nodename']
        except KeyError:
            nodename = " "
        try:

            if output['status'] == 'resolved':
                # 恢复模板
                send_data = alert_data(output, nodename, "恢复", 1)

            else:
                # 报警模板
                send_data = alert_data(output, nodename, "告警", 1)
        except KeyError:
            # mq报警恢复
            if output['status'] == 'resolved':
                nodename = ""
                send_data = alert_data(output, nodename, "恢复", 0)
            else:
                if output['labels']['Cluster'] == 'pro-mq':
                    nodename = ""
                    send_data = alert_data(output, nodename, "告警", 0)

        req = requests.post(url, headers=headers, json=send_data)
        result = req.json()
        if result['errcode'] != 0:
            print('notify dingtalk error: %s' % result['errcode'])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
