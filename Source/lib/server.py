# This is a server script.
import paramiko
import os
import json
import xml.etree.ElementTree as ET
from cryptography.fernet import Fernet
from Source.lib.send_email import send_mail
from Source.lib import config as cf


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
    return '\n'.join(s)


CRYPTO_KEY = b'mWK49Y-bLpaycw7xXaTO_IoFs_8vBeQtSepE0qbIva8='


def run(xml_path):
    config = XMLConfig(xml_path)
    config_obj = config.parse2obj()
    email_to_list = [config_obj['info']['mail'], ]
    conn = SSHConnection(config_obj['info'])
    tmp_dirname = b'/tmp/sysinfo'
    conn.exec_command(b'mkdir ' + tmp_dirname)
    source_path = 'client.py'
    client_path = tmp_dirname + b'/client.py'
    conn.upload_file(source_path, client_path)
    cmd = [cf.CLIENT_PYTHON_PATH, client_path]
    stdoutdata, stderrdata = conn.exec_command(b' '.join(cmd))
    if stderrdata:
        raise Exception("Error occure when get infomation in client : %s. Error info: %s" % \
                        (config_obj['info']['ip'], stderrdata))
    plain_text = Fernet(CRYPTO_KEY).decrypt(stdoutdata)
    sysinfo = json.loads(plain_text.decode())
    print(sysinfo)
    email_content = parse2text(sysinfo)
    print(email_content)
    # send_mail(email_content, 'System Info', email_to_list)
    conn.close()


def main():
    import threading
    import glob
    conf_dir = os.path.join(os.path.dirname(__file__), '../example/data')
    conf_pattern = conf_dir + '/*.xml'
    xml_files = glob.glob(conf_pattern)
    for f in xml_files:
        t = threading.Thread(target=run, args=(f, ))
        t.start()

if __name__ == '__main__':
    run('../example/data/conf1.xml')