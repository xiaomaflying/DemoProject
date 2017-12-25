# This is a server script.
import paramiko
import os


config_dir = '/tmp/sysinfo_conf'
client_conf = os.path.join(config_dir, 'conf.xml')


def upload_file():
    t = paramiko.Transport(('localhost', 22))
    t.connect(username='maxinmin', password='maxinmin')
    sftp = paramiko.SFTPClient.from_transport(t)

    client_script = os.path.join(os.path.dirname(__file__), 'client.py')
    remote_path = '/tmp/client.py'

    sftp.put(client_script, remote_path)

def mkdir_remote():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect("localhost", 22, "maxinmin", "maxinmin")
    stdin, stdout, stderr = ssh.exec_command("mkdir /tmp/fuck")
    print
    stdout.readlines()
    ssh.close()


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
        print
        print(stdout.readlines())

    def close(self):
        self.ssh.close()
        self.sftp.close()


import xml.etree.ElementTree as ET
class XMLConfig:
    def __init__(self, xml_path):
        self.path = xml_path

    def parse2obj(self):
        tree = ET.parse(self.path)
        root = tree.getroot()
        alerts = [child.attrib for child in root]
        result = {'info': root.attrib, 'alerts': alerts}
        return result


config = XMLConfig('/tmp/sysinfo_conf/conf.xml')
config_obj = config.parse2obj()
# print(config_obj)
conn = SSHConnection(config_obj['info'])
# conn.exec_command('ls -alh ~')
source_path = os.path.join(os.path.dirname(__file__), 'server.py')
conn.upload_file(source_path, '/tmp/sysinfo_conf/server.py')
conn.close()