from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from python_on_whales import DockerClient  # type: ignore[import-not-found]
else:
    try:
        from python_on_whales import DockerClient
    except ImportError:
        DockerClient = None
import os
import tempfile


class CustomClient:
    _verbose = False

    def __init__(self, verbose: bool):
        self._verbose = verbose

    def __str__(self):
        return "DOCKER_CLIENT"

    def _logger(self, string):
        if self._verbose:
            print(f"[{self}]: {string}")

    def run(
        self,
        service: str,
        compose_file: str,
        version: str,
        host_uid: Optional[int] = None,
        host_gid: Optional[int] = None,
    ) -> bool:
        host_uid = host_uid or os.getuid()
        host_gid = host_gid or os.getgid()

        printer = f"""Env variables:
            HOST_UID {host_uid}
            HOST_GID {host_gid}
            {version}
        """

        self._logger(printer)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write(f"HOST_UID={host_uid}\n")
            f.write(f"HOST_GID={host_gid}\n")
            f.write(f"{version}\n")  # This will be for example PG_VERSION=16.1
            env_file = f.name

        try:
            client = DockerClient(
                compose_files=[compose_file],
                compose_env_files=[env_file],
                client_call=["docker"],
            )
            # IMPORTANT, client.compose.build is needed
            # otherwise it does not detect different versions passed as env variables
            # It will cache anyway same versions.
            # Example 16.1 if compiled already, passing 16.1 again will use cached old binaries
            # Instead, if i pass 18.3 it will recompile and cache this
            client.compose.build(
                services=[service]
            )  # option: no_cache=True -> too aggressive, recompiles everything everytime
            client.compose.up(services=[service])
        except Exception as ex:
            if self._verbose:
                self._logger(ex)
                return False
        finally:
            os.unlink(env_file)

        return True
