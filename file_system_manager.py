import math

from fs_constants import FsConstants
from directory_entry import DirectoryEntry
from directory_manager import DirectoryManager
from fat_table_manager import FatTableManager


class FileSystem:
    def __init__(self, virtual_disk):
        self.disk = virtual_disk
        self.dir_manager = DirectoryManager(virtual_disk)
        self.fat_manager = FatTableManager(virtual_disk)

    def create_file(self, parent_cluster, filename):
        existing = self.dir_manager.find_directory_entry(parent_cluster, filename)

        if existing is not None:
            raise Exception("File already exists")

        entry = DirectoryEntry(
            name=filename,
            attr=0,
            first_cluster=0,
            file_size=0
        )

        self.dir_manager.add_directory_entry(parent_cluster, entry)

    def write_file(self, parent_cluster, filename, data):
        entry = self.dir_manager.find_directory_entry(parent_cluster, filename)

        if entry is None:
            raise Exception("File not found")

        if isinstance(data, str):
            data = data.encode("utf-8")

        if entry.first_cluster not in [0, -1]:
            self.fat_manager.free_chain(entry.first_cluster)

        required_clusters = math.ceil(len(data) / FsConstants.CLUSTER_SIZE)

        if required_clusters == 0:
            entry.first_cluster = 0
            entry.file_size = 0
            return

        first_cluster = self.fat_manager.allocate_chain(required_clusters)

        chain = self.fat_manager.follow_chain(first_cluster)

        offset = 0

        for cluster in chain:
            chunk = data[offset:offset + FsConstants.CLUSTER_SIZE]

            if len(chunk) < FsConstants.CLUSTER_SIZE:
                chunk += b'\x00' * (FsConstants.CLUSTER_SIZE - len(chunk))

            self.disk.write_cluster(cluster, chunk)

            offset += FsConstants.CLUSTER_SIZE

        entry.first_cluster = first_cluster
        entry.file_size = len(data)

        self._update_entry(parent_cluster, entry)

    def read_file(self, file_entry):
        if file_entry.first_cluster == 0:
            return b""

        chain = self.fat_manager.follow_chain(file_entry.first_cluster)

        data = bytearray()

        for cluster in chain:
            data.extend(self.disk.read_cluster(cluster))

        return bytes(data[:file_entry.file_size])

    def delete_file(self, parent_cluster, filename):
        entry = self.dir_manager.find_directory_entry(parent_cluster, filename)

        if entry is None:
            raise Exception("File not found")

        if entry.first_cluster not in [0, -1]:
            self.fat_manager.free_chain(entry.first_cluster)

        self.dir_manager.remove_directory_entry(parent_cluster, filename)

    def rename_entry(self, directory_cluster, old_name, new_name):
        old_entry = self.dir_manager.find_directory_entry(directory_cluster, old_name)

        if old_entry is None:
            raise Exception("Entry not found")

        existing = self.dir_manager.find_directory_entry(directory_cluster, new_name)

        if existing is not None:
            raise Exception("Name already exists")

        self.dir_manager.remove_directory_entry(directory_cluster, old_name)

        old_entry.name = DirectoryEntry.format_name_to_8dot3(new_name)

        self.dir_manager.add_directory_entry(directory_cluster, old_entry)

    def copy_file(self, src_entry, dest_parent_cluster, dest_name):
        existing = self.dir_manager.find_directory_entry(dest_parent_cluster, dest_name)

        if existing is not None:
            raise Exception("Destination already exists")

        data = self.read_file(src_entry)

        new_entry = DirectoryEntry(
            name=dest_name,
            attr=0,
            first_cluster=0,
            file_size=0
        )

        self.dir_manager.add_directory_entry(dest_parent_cluster, new_entry)

        self.write_file(dest_parent_cluster, dest_name, data)

    def move_file(self, src_parent_cluster, src_name, dest_parent_cluster, dest_name):
        entry = self.dir_manager.find_directory_entry(src_parent_cluster, src_name)

        if entry is None:
            raise Exception("Source file not found")

        self.copy_file(entry, dest_parent_cluster, dest_name)

        self.delete_file(src_parent_cluster, src_name)

    def create_directory(self, parent_cluster, dirname):
        existing = self.dir_manager.find_directory_entry(parent_cluster, dirname)

        if existing is not None:
            raise Exception("Directory already exists")

        first_cluster = self.fat_manager.allocate_chain(1)

        empty_cluster = b'\x00' * FsConstants.CLUSTER_SIZE

        self.disk.write_cluster(first_cluster, empty_cluster)

        entry = DirectoryEntry(
            name=dirname,
            attr=1,
            first_cluster=first_cluster,
            file_size=0
        )

        self.dir_manager.add_directory_entry(parent_cluster, entry)

    def remove_directory(self, parent_cluster, dirname):
        entry = self.dir_manager.find_directory_entry(parent_cluster, dirname)

        if entry is None:
            raise Exception("Directory not found")

        if entry.attr != 1:
            raise Exception("Not a directory")

        entries = self.dir_manager.read_directory(entry.first_cluster)

        if len(entries) > 0:
            raise Exception("Directory is not empty")

        self.fat_manager.free_chain(entry.first_cluster)

        self.dir_manager.remove_directory_entry(parent_cluster, dirname)

    def _update_entry(self, parent_cluster, updated_entry):
        clusters = self.fat_manager.follow_chain(parent_cluster)

        for cluster in clusters:
            cluster_data = bytearray(self.disk.read_cluster(cluster))

            for i in range(0, FsConstants.CLUSTER_SIZE, 32):
                entry_data = cluster_data[i:i + 32]

                entry = DirectoryEntry.from_bytes(entry_data)

                if entry is not None:
                    if entry.name == updated_entry.name:

                        cluster_data[i:i + 32] = updated_entry.to_bytes()

                        self.disk.write_cluster(cluster, bytes(cluster_data))

                        return