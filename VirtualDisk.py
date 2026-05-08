import os

class VirtualDisk:
    def __init__(self, path, create_if_missing=True):
        self.path = path
        self.cluster_size = 1024
        self.cluster_count = 1024
        self.disk_size = self.cluster_size * self.cluster_count
        self.file_handle = None
        self._initialize(create_if_missing)

    def _initialize(self, create_if_missing):
        if create_if_missing and not os.path.exists(self.path):
            with open(self.path, 'wb') as f:
                f.write(b'\x00' * self.disk_size)
        self.file_handle = open(self.path, 'r+b')

    def read_cluster(self, cluster_number):
        if cluster_number < 0 or cluster_number >= self.cluster_count:
            raise ValueError(f"Invalid cluster number: {cluster_number}")
        offset = cluster_number * self.cluster_size
        self.file_handle.seek(offset)
        data = self.file_handle.read(self.cluster_size)
        if len(data) != self.cluster_size:
            raise IOError(f"Read {len(data)} bytes, expected {self.cluster_size}")
        return data

    def write_cluster(self, cluster_number, data):
        if cluster_number < 0 or cluster_number >= self.cluster_count:
            raise ValueError(f"Invalid cluster number: {cluster_number}")
        if len(data) != self.cluster_size:
            raise ValueError(f"Data length {len(data)} != {self.cluster_size}")
        offset = cluster_number * self.cluster_size
        self.file_handle.seek(offset)
        self.file_handle.write(data)
        self.file_handle.flush()

    def get_disk_size(self):
        return self.disk_size

    def close_disk(self):
        if self.file_handle:
            self.file_handle.close()
            self.file_handle = None

    def __del__(self):
        self.close_disk()