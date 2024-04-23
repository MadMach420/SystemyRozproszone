import ray
import textwrap
import random


NAMESPACE = "storage"
NAME = "name_node"
CHUNK_SIZE = 10  # Deliberately small to showcase splitting into chunks
CHUNK_COPIES = 3


@ray.remote
class NameNode:
    def __init__(self):
        self.next_node_id = 0
        self.storage_nodes = {}
        self.artifacts = {}

    def init_storage(self, storage_node):
        current_id = self.next_node_id
        self.storage_nodes[current_id] = storage_node
        self.next_node_id += 1
        print(f"Storage node created, ID: {current_id}")
        return current_id

    def list_artifacts(self):
        return self.artifacts

    def new_artifact(self, name, content):
        self.artifacts[name] = {}
        chunks = textwrap.wrap(content, CHUNK_SIZE, replace_whitespace=False, drop_whitespace=False)
        for i, chunk in enumerate(chunks):
            self.save_chunk(name, i, chunk)
        return f"Artifact {name} created"

    def update_artifact(self, name, content):
        if name not in self.artifacts.keys():
            return "Artifact does not exist"
        else:
            self.new_artifact(name, content)
            return f"Artifact {name} updated"

    def delete_artifact(self, name):
        for chunk_number in self.artifacts[name]:
            self.delete_chunk(name, chunk_number)
        del self.artifacts[name]
        return f"Artifact {name} deleted"

    def get_artifact(self, name):
        chunks = [f"{name}: "]
        for chunk_number in self.artifacts[name]:
            print(chunk_number)
            chunks.append(self.get_chunk(name, chunk_number))
        return "".join(chunks)

    def save_chunk(self, name, number, chunk):
        nodes = self.get_nodes_to_save()
        for node_num in nodes:
            node = self.storage_nodes[node_num]
            node.save_chunk.remote(name, number, chunk)
        self.artifacts[name][number] = nodes

    def delete_chunk(self, name, number):
        for node_number in self.artifacts[name][number]:
            try:
                node = self.storage_nodes[node_number]
                node.delete_chunk.remote(name, number)
            except:
                pass

    def get_chunk(self, name, number):
        for node_number in self.artifacts[name][number]:
            try:
                node = self.storage_nodes[node_number]
                return ray.get(node.get_chunk.remote(name, number))
            except:
                print(f'Node {self.storage_nodes[node_number]} failed')
                pass

    def get_nodes_to_save(self) -> list:
        if len(self.storage_nodes) <= CHUNK_COPIES:
            return list(self.storage_nodes.keys())
        else:
            return random.sample(self.storage_nodes.keys(), CHUNK_COPIES)


def read_commands(name_node):
    while True:
        user_input = input("> ")
        user_input = user_input.split(";")
        try:
            if user_input[0].lower() == "new":
                ray_id = name_node.new_artifact.remote(user_input[1], user_input[2])
            elif user_input[0].lower() == "get":
                ray_id = name_node.get_artifact.remote(user_input[1])
            elif user_input[0].lower() == "delete":
                ray_id = name_node.delete_artifact.remote(user_input[1])
            elif user_input[0].lower() == "update":
                ray_id = name_node.update_artifact.remote(user_input[1], user_input[2])
            elif user_input[0].lower() == "list":
                ray_id = name_node.list_artifacts.remote()
            elif user_input[0].lower() == "exit":
                break
            else:
                print("Available commands:")
                print("  - new;<name>;<content> - create a new artifact")
                print("  - get;<name> - get a specific artifact")
                print("  - delete;<name> - delete a specific artifact")
                print("  - update;<name>;<content> - update a specific artifact")
                print("  - list - list all available artifacts")
                print("  - exit - end session")
                raise ValueError
            print(ray.get(ray_id))
        except (KeyError, ValueError):
            print("Invalid input")
            pass


if __name__ == "__main__":
    ray.init(address="auto", namespace=NAMESPACE)
    name_node = NameNode.options(name=NAME, get_if_exists=True).remote()
    read_commands(name_node)
