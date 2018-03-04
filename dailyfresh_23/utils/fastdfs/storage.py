from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client
from django.conf import settings


class FastDFSStorage(Storage):

    def __init__(self, client_conf=None, server_ip=None):
        if client_conf is None:
            client_conf = settings.CLIENT_CONF
        self.client_conf = client_conf
        if server_ip is None:
            server_ip = settings.SERVER_IP
        self.server_ip = server_ip

    def _open(self, name, mode='rb'):

        pass

    def _save(self, name, content):

        client = Fdfs_client(self.client_conf)
        file_data = content.read()
        try:
            result = client.upload_by_buffer(file_data)
        except Exception as e:
            print(e)
            raise
        if result.get('Status') == 'Upload successed.':
            file_id = result.get('Remote file_id')
            return file_id
        else:
            raise Exception('上传文件到fdfs失败')

    def exists(self, name):
        return False

    def url(self, name):
        return self.server_ip + name

