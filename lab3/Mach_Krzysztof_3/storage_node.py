import sys

import ray
from name_node import NAMESPACE, NAME, NameNode


@ray.remote
class StorageNode:
    def __init__(self):
        self.chunks = {}

    def save_chunk(self, name, number, chunk):
        if name not in self.chunks.keys():
            self.chunks[name] = {}
        self.chunks[name][number] = chunk

    def delete_chunk(self, name, number):
        del self.chunks[name][number]

    def get_chunk(self, name, number):
        return self.chunks[name][number]


if __name__ == '__main__':
    ray.init(address="auto", namespace=NAMESPACE)

    num_of_nodes = int(input("How many storage nodes do you want to create? "))
    nodes = []
    for i in range(num_of_nodes):
        name_node = NameNode.options(name=NAME, get_if_exists=True).remote()
        storage_node = StorageNode.remote()
        node_id = name_node.init_storage.remote(storage_node)
        nodes.append(node_id)
    ray.get(nodes)
    print(f"Storage nodes created")

    while True:
        pass  # To keep nodes alive
