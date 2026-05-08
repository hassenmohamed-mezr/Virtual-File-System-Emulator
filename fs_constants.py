
class FsConstants:

    # Size of one cluster in bytes
    CLUSTER_SIZE = 1024

    # Total number of clusters in disk
    CLUSTER_COUNT = 1024

    # Superblock location
    SUPERBLOCK_CLUSTER = 0

    # FAT region
    FAT_START_CLUSTER = 1
    FAT_END_CLUSTER = 4

    # Root directory cluster
    ROOT_DIR_FIRST_CLUSTER = 5

    # Data/content region
    CONTENT_START_CLUSTER = 6


class SuperblockManager:
    def __init__(self, virtual_disk):
        self.disk = virtual_disk

    def read_superblock(self):
        return self.disk.read_cluster(FsConstants.SUPERBLOCK_CLUSTER)

    def write_superblock(self, data):
        if len(data) != FsConstants.CLUSTER_SIZE:
            raise ValueError(f"Data must be exactly {FsConstants.CLUSTER_SIZE} bytes")
        self.disk.write_cluster(FsConstants.SUPERBLOCK_CLUSTER, data)


def init_superblock_on_new_disk(virtual_disk):
    mgr = SuperblockManager(virtual_disk)
    mgr.write_superblock(b'\x00' * FsConstants.CLUSTER_SIZE)    