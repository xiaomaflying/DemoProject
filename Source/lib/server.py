# This is a server script.
import paramiko
import os
import json
import sys
import xml.etree.ElementTree as ET
from cryptography.fernet import Fernet
from Source.lib.send_email import send_mail
from Source.lib import config as cf
from Source.lib.db import DBConnector


class SSHConnection:

    def __init__(self, config):
        host = config['ip']
        port = int(config.get('port', 22))
        user = config['username']
        passwd = config['password']
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(host, port, user, passwd)

        t = paramiko.Transport((host, port))
        t.connect(username=user, password=passwd)
        self.sftp = paramiko.SFTPClient.from_transport(t)

    def upload_file(self, source, target):
        if os.path.exists(source):
            self.sftp.put(source, target)
        else:
            raise Exception('%s not found' % source)

    def exec_command(self, command):
        stdin, stdout, stderr = self.ssh.exec_command(command)
        return stdout.read(), stderr.read()

    def close(self):
        self.ssh.close()
        self.sftp.close()


class XMLConfig:
    def __init__(self, xml_path):
        self.path = xml_path

    def _check_xml_attrs(self, d):
        userinfo = d['info']
        args_required = ['ip', 'username', 'password', 'mail']
        for arg in args_required:
            if not arg in userinfo:
                raise ValueError("%s must be one of client attributes")

    def parse2obj(self):
        try:
            tree = ET.parse(self.path)
        except:
            raise TypeError('Xml file is illegal: %s' % self.path)
        root = tree.getroot()
        alerts = [child.attrib for child in root]
        result = {'info': root.attrib, 'alerts': alerts}
        self._check_xml_attrs(result)
        return result

def parse2text(d):
    s = []
    s.append("<p>Memory Percent: %.2f%%</p>" % d.get('mem_percent'))
    s.append("<p>CPU Percent: %.2f%%</p>" % d.get('cpu_percent'))
    s.append("<p>Uptime: %ds</p>" % int(d.get('uptime')))
    s.append("<div>%s</div>" % d.get('log_content'))
    return '\n'.join(s)


CRYPTO_KEY = b'mWK49Y-bLpaycw7xXaTO_IoFs_8vBeQtSepE0qbIva8='


def run(xml_path):
    config = XMLConfig(xml_path)
    config_obj = config.parse2obj()
    email_to_list = [config_obj['info']['mail'], ]
    conn = SSHConnection(config_obj['info'])
    tmp_dirname = b'SysInfo'
    conn.exec_command(b'mkdir ' + tmp_dirname)
    scripts = [b'get_windows_events.py', b'client.py', ]
    for script in scripts:
        client_path = b'%s/%s' % (tmp_dirname, script)
        conn.upload_file(script, client_path)

        cmd = [b'python', client_path]
        stdoutdata, stderrdata = conn.exec_command(b' '.join(cmd))
        # print(stdoutdata, stderrdata)

    if stderrdata:
        raise Exception("Error occure when get infomation in client : %s. Error info: %s" % \
                        (config_obj['info']['ip'], stderrdata))
    plain_text = Fernet(CRYPTO_KEY).decrypt(stdoutdata)
    sysinfo = json.loads(plain_text.decode())
    # print(sysinfo)
    email_content = parse2text(sysinfo)
    # print(email_content)

    # insert into database
    connector = DBConnector(cf.DB_CONFIG)
    info = config_obj['info']
    connector.execute_insert_sql(info['ip'], info['username'], info['email'], sysinfo)
    connector.close()

    send_mail(email_content, 'System Info', email_to_list)
    conn.close()


def main(conf_dir):
    import threading
    import glob
    conf_pattern = conf_dir + '/*.xml'
    xml_files = glob.glob(conf_pattern)
    for f in xml_files:
        t = threading.Thread(target=run, args=(f, ))
        t.start()


if __name__ == '__main__':
    run('../data/conf1.xml')
    # if len(sys.argv) != 2:
    #     print('Usage: PYTHONPATH=../../ python3 server.py ../data')
    #     exit(1)
    # main(sys.argv[1])