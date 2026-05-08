from VirtualDisk import VirtualDisk
from fs_constants import FsConstants
from converter import converters



class FatTableManager:
    def __init__(self, virtual_disk):
        self.disk = virtual_disk
        self.fat = [0] * FsConstants.CLUSTER_COUNT
        self.load_fat_from_disk()

        if self.fat[FsConstants.ROOT_DIR_FIRST_CLUSTER] == 0:
            self.initialize_fat()

    def initialize_fat(self):

        for i in range(FsConstants.CONTENT_START_CLUSTER):
            self.fat[i] = -1

        self.fat[FsConstants.ROOT_DIR_FIRST_CLUSTER] = -1

        self.flush_fat_to_disk()

    def load_fat_from_disk(self):
        data = bytearray()
        for cluster in range(FsConstants.FAT_START_CLUSTER, FsConstants.FAT_END_CLUSTER + 1):
            data.extend(self.disk.read_cluster(cluster))
        
        for i in range(FsConstants.CLUSTER_COUNT):
            start = i * 4
            self.fat[i] = converters.BytesToInt(data[start:start+4])

    def flush_fat_to_disk(self):
        fat_bytes = bytearray()
        for entry in self.fat:
            fat_bytes.extend(converters.IntToBytes(entry))
        
        for cluster in range(FsConstants.FAT_START_CLUSTER, FsConstants.FAT_END_CLUSTER + 1):
            start_offset = (cluster - FsConstants.FAT_START_CLUSTER) * FsConstants.CLUSTER_SIZE
            self.disk.write_cluster(cluster, fat_bytes[start_offset:start_offset + FsConstants.CLUSTER_SIZE])

    def get_fat_entry(self, index):
        if index < 0 or index >= FsConstants.CLUSTER_COUNT:
            raise ValueError("Invalid cluster index")
        return self.fat[index]

    def set_fat_entry(self, index, value):
        if index < 0 or index >= FsConstants.CLUSTER_COUNT:
            raise ValueError("Invalid cluster index")
        if index <= FsConstants.FAT_END_CLUSTER and value != 0:
            raise ValueError("Cannot allocate reserved cluster")
        self.fat[index] = value

    def read_all_fat(self):
        return self.fat.copy()

    def follow_chain(self, start_cluster):
        if start_cluster < 0 or start_cluster >= FsConstants.CLUSTER_COUNT:
            raise ValueError("Invalid start cluster")
        chain = []
        current = start_cluster
        while current != -1:
            if current in chain:
                raise ValueError("Cycle detected in FAT chain")
            chain.append(current)
            current = self.fat[current]
            if current != -1 and (current < 0 or current >= FsConstants.CLUSTER_COUNT):
                raise ValueError("Invalid cluster pointer in FAT")
        return chain

    def allocate_chain(self, required_clusters):
        if required_clusters <= 0:
            raise ValueError("Required clusters must be positive")
        
        free_clusters = []
        for i in range(FsConstants.CONTENT_START_CLUSTER, FsConstants.CLUSTER_COUNT):
            if self.fat[i] == 0:
                free_clusters.append(i)
                if len(free_clusters) == required_clusters:
                    break
        
        if len(free_clusters) < required_clusters:
            raise Exception("Not enough free clusters")
        
        for idx, cluster in enumerate(free_clusters):
            if idx == required_clusters - 1:
                self.fat[cluster] = -1
            else:
                self.fat[cluster] = free_clusters[idx + 1]
        
        self.flush_fat_to_disk()
        return free_clusters[0]

    def free_chain(self, start_cluster):
        if start_cluster < 0 or start_cluster >= FsConstants.CLUSTER_COUNT:
            raise ValueError("Invalid start cluster")
        
        chain = self.follow_chain(start_cluster)
        for cluster in chain:
            self.fat[cluster] = 0
        
        self.flush_fat_to_disk()