import ray

from name_node import NameNode, NAME, NAMESPACE
from storage_node import StorageNode

if __name__ == '__main__':
    ray.init(address="auto", namespace=NAMESPACE)
    name_node = NameNode.options(name=NAME, get_if_exists=True).remote()

    nodes = []
    for i in range(5):
        storage_node = StorageNode.remote()
        node_id = name_node.init_storage.remote(storage_node)
        nodes.append(node_id)
    ray.get(nodes)

    # time.sleep(20)  # Żeby podłączyć w tym czasie storage nodes
    status_id = name_node.list_artifacts.remote()
    print(f'Status: {ray.get(status_id)}')
    name_node.new_artifact.remote("test1", "Test artifact")
    status_id = name_node.list_artifacts.remote()
    print(f'Status: {ray.get(status_id)}')
    name_node.update_artifact.remote("test1", "Updated artifact")
    status_id = name_node.list_artifacts.remote()
    print(f'Status: {ray.get(status_id)}')
    id = name_node.get_artifact.remote("test1")
    print(f'Got artifact: {ray.get(id)}')
    status_id = name_node.list_artifacts.remote()
    print(f'Status: {ray.get(status_id)}')
    id = name_node.delete_artifact.remote("test1")
    ray.get(id)
    status_id = name_node.list_artifacts.remote()
    print(f'Status: {ray.get(status_id)}')