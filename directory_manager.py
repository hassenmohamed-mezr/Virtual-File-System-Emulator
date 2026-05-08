from fs_constants import FsConstants
from converter import converters
from fat_table_manager import FatTableManager


class DirectoryEntry:
    ENTRY_SIZE = 32

    def __init__(self, name="", attr=0, first_cluster=-1, file_size=0):
        self.name = self.format_name_to_8dot3(name)
        self.attr = attr
        self.first_cluster = first_cluster
        self.file_size = file_size

    @staticmethod
    def format_name_to_8dot3(name):
        name = name.upper()

        if "." in name:
            filename, extension = name.split(".", 1)
        else:
            filename = name
            extension = ""

        filename = filename[:8].ljust(8)
        extension = extension[:3].ljust(3)

        return filename + extension

    @staticmethod
    def parse_8dot3_name(raw_name):
        filename = raw_name[:8].strip()
        extension = raw_name[8:11].strip()

        if extension:
            return f"{filename}.{extension}"

        return filename

    def to_bytes(self):
        data = bytearray(32)

        data[0:11] = self.name.encode("ascii")
        data[11] = self.attr

        data[12:16] = converters.IntToBytes(self.first_cluster)
        data[16:20] = converters.IntToBytes(self.file_size)

        return bytes(data)

    @staticmethod
    def from_bytes(data):
        if data[0] == 0x00:
            return None

        raw_name = data[0:11].decode("ascii")

        attr = data[11]

        first_cluster = converters.BytesToInt(data[12:16])
        file_size = converters.BytesToInt(data[16:20])

        entry = DirectoryEntry()

        entry.name = raw_name
        entry.attr = attr
        entry.first_cluster = first_cluster
        entry.file_size = file_size

        return entry


class DirectoryManager:
    def __init__(self, virtual_disk):
        self.disk = virtual_disk
        self.fat_manager = FatTableManager(virtual_disk)

    def read_directory(self, start_cluster):
        clusters = self.fat_manager.follow_chain(start_cluster)

        entries = []

        for cluster in clusters:
            cluster_data = self.disk.read_cluster(cluster)

            for i in range(0, FsConstants.CLUSTER_SIZE, 32):
                entry_data = cluster_data[i:i + 32]

                entry = DirectoryEntry.from_bytes(entry_data)

                if entry is not None:
                    entries.append(entry)

        return entries

    def find_directory_entry(self, start_cluster, name):
        name = DirectoryEntry.format_name_to_8dot3(name)

        clusters = self.fat_manager.follow_chain(start_cluster)

        for cluster in clusters:
            cluster_data = bytearray(self.disk.read_cluster(cluster))

            for i in range(0, FsConstants.CLUSTER_SIZE, 32):
                entry_data = cluster_data[i:i + 32]

                entry = DirectoryEntry.from_bytes(entry_data)

                if entry is not None:
                    if entry.name.upper() == name.upper():
                        return entry

        return None

    def add_directory_entry(self, start_cluster, entry):
        clusters = self.fat_manager.follow_chain(start_cluster)

        for cluster in clusters:
            cluster_data = bytearray(self.disk.read_cluster(cluster))

            for i in range(0, FsConstants.CLUSTER_SIZE, 32):
                if cluster_data[i] == 0x00:
                    cluster_data[i:i + 32] = entry.to_bytes()

                    self.disk.write_cluster(cluster, bytes(cluster_data))

                    return

        new_cluster = self.fat_manager.allocate_chain(1)

        last_cluster = clusters[-1]

        self.fat_manager.set_fat_entry(last_cluster, new_cluster)
        self.fat_manager.set_fat_entry(new_cluster, -1)

        self.fat_manager.flush_fat_to_disk()

        new_cluster_data = bytearray(FsConstants.CLUSTER_SIZE)

        new_cluster_data[0:32] = entry.to_bytes()

        self.disk.write_cluster(new_cluster, bytes(new_cluster_data))

    def remove_directory_entry(self, start_cluster, name):
        name = DirectoryEntry.format_name_to_8dot3(name)

        clusters = self.fat_manager.follow_chain(start_cluster)

        for cluster in clusters:
            cluster_data = bytearray(self.disk.read_cluster(cluster))

            for i in range(0, FsConstants.CLUSTER_SIZE, 32):
                entry_data = cluster_data[i:i + 32]

                entry = DirectoryEntry.from_bytes(entry_data)

                if entry is not None:
                    if entry.name.upper() == name.upper():

                        if entry.first_cluster != -1:
                            self.fat_manager.free_chain(entry.first_cluster)

                        cluster_data[i:i + 32] = b'\x00' * 32

                        self.disk.write_cluster(cluster, bytes(cluster_data))

                        return True

        return False

    def list_root_directory(self):
        return self.read_directory(FsConstants.ROOT_DIR_FIRST_CLUSTER)