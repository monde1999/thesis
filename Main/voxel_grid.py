import numpy as np
from soupsieve import select


p1 = 73856093
p2 = 19349669
p3 = 83492791
n = 10

def hash(position):
    # position : [x,y,z]
    return ((position[0] * p1) ^ (position[1] * p2) ^ (position[2] * p3)) % n

class VoxelGrid:
    def __init__(self):
        self.grid = np.full(n, None)
    
    def insert(self, position, voxel):
        key = hash(position)
        bucket = self.grid[key]
        if bucket is not None:
            flag = True
            for hash_entry in bucket:
                if hash_entry[0]==position:
                    flag = False
                    break
            if flag: self.grid[key].append([position,voxel])
        else:
            self.grid[key] = [[position,voxel]]
        # hash entry: [location, voxel]
    def retrieve(self, position):
        key = hash(position)
        bucket = self.grid[key]
        res = None
        if bucket is not None:
            for hash_entry in bucket:
                if hash_entry[0]==position:
                    res = hash_entry[1]
                    break
        return res
    def delete(self, position):
        key = hash(position)
        bucket = self.grid[key]
        if bucket is not None:
            index = -1
            hash_entry_index = None
            for hash_entry in bucket:
                index += 1
                if hash_entry[0]==position:
                    hash_entry_index = index
                    break
            if hash_entry_index is not None:
                bucket.pop(hash_entry_index)
    def get_voxels(self):
        return self.grid[self.grid != None]
    
# vg = VoxelGrid()
# vg.insert([1,2,3],[100,101,102])
# print(vg.retrieve([1,2,3]))
# vg.delete([1,2,3])
# print(vg.retrieve([1,2,3]))
# vg.insert([1,2,3],[100,101,102])
# vg.insert([1,2,3],[100,101,102])
# print(vg.get_voxels())