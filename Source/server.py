# This is a server script.
import paramiko
import os


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
