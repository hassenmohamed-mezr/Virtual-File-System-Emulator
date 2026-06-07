from fs_constants import FsConstants
from converter import converters


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
