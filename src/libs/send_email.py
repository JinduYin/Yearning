
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
import requests
from libs import util

conf = util.conf_path()
from_addr = conf.mail_user
# password = conf.password
smtp_server = conf.smtp
smtp_port = conf.smtp_port

# from_addr = 'tcjfsor_service@ly.com'
# smtp_server =  'mail.ly.com'
# smtp_port = 25


class send_email(object):

    def __init__(self, to_addr=None):
        self.to_addr = to_addr
        self.pwd = get_password(from_addr)

    def _format_addr(self, s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr))

    def send_mail(self,mail_data=None,type=None):
        if type == 0: #同意
            text = '<html><body><h1>TCSQL 工单同意通知</h1>' \
                   '<br><p>工单号: %s</p>' \
                   '<br><p>发起人: %s</p>' \
                   '<br><p>地址: <a href="%s">%s</a></p>' \
                   '<br><p>工单备注: %s</p>' \
                   '<br><p>状态: 同意</p>' \
                   '<br><p>备注: %s</p>' \
                   '</body></html>' %(
                mail_data['workid'],
                mail_data['to_user'],
                mail_data['addr'],
                mail_data['addr'],
                mail_data['text'],
                mail_data['note'])
        elif type == 1: #驳回
            text = '<html><body><h1>TCSQL 工单驳回通知</h1>' \
                   '<br><p>工单号: %s</p>' \
                   '<br><p>发起人: %s</p>' \
                   '<br><p>地址: <a href="%s">%s</a></p>' \
                   '<br><p>状态: 驳回</p>' \
                   '<br><p>驳回说明: %s</p>' \
                   '</body></html>' % (
                       mail_data['workid'],
                       mail_data['to_user'],
                       mail_data['addr'],
                       mail_data['addr'],
                       mail_data['rejected'])
        else: #提交
            text = '<html><body><h1>TCSQL 工单提交通知</h1>' \
                   '<br><p>工单号: %s</p>' \
                   '<br><p>发起人: %s</p>' \
                   '<br><p>地址: <a href="%s">%s</a></p>' \
                   '<br><p>工单备注: %s</p>' \
                   '<br><p>状态: 已提交</p>' \
                   '<br><p>备注: %s</p>' \
                   '</body></html>' % (
                       mail_data['workid'],
                       mail_data['to_user'],
                       mail_data['addr'],
                       mail_data['addr'],
                       mail_data['text'],
                       mail_data['note'])
        msg = MIMEText(text, 'html', 'utf-8')
        msg['From'] = self._format_addr('TCSQL <%s>' % from_addr)
        msg['To'] = self._format_addr('%s' % self.to_addr)
        msg['Subject'] = Header('TCSQL 工单消息推送', 'utf-8').encode()

        server = smtplib.SMTP(smtp_server, int(smtp_port))
        server.set_debuglevel(1)
        server.login(from_addr, self.pwd)
        server.sendmail(from_addr, [self.to_addr], msg.as_string())
        server.quit()


def get_password(email='tcjfsor_service@ly.com'):
    response = requests.request(
        method='GET',
        url='http://cmdbapi.jrlab.17usoft.com/cmdb/email',
        params=dict(email=email)
    )
    if response.status_code == 200:
        data = response.json()
        results = data.get('results')
        if len(results):
            return results[0].get('password')

    return ''


if __name__ == '__main__':
    res = dict(
        workid=11111,
        to_user='test',
        addr='22222',
        text='4444',
        note='4444'
    )
    put_mess = send_email('yjd48676@ly.com')
    put_mess.send_mail(mail_data=res, type=2)
    # print(get_password())