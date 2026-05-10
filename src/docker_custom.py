from python_on_whales import DockerClient
import os, tempfile

class CustomClient:
    _verbose = False

    def __init__(self, verbose: bool):
        self._verbose = verbose

    def run(self, service: str, compose_file: str, host_uid: int = None, host_gid: int = None) -> bool:
        host_uid = host_uid or os.getuid()
        host_gid = host_gid or os.getgid()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(f"HOST_UID={host_uid}\n")
            f.write(f"HOST_GID={host_gid}\n")
            env_file = f.name

        try:
            client = DockerClient(compose_files=[compose_file], compose_env_files=[env_file])
            client.compose.up(services=[service])
        except Exception as ex:
            if self._verbose:
                print(ex)
                return False
        finally:
            os.unlink(env_file)


        return True