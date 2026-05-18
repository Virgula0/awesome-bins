from postgre import postgre
from vim import vim
from netcat_traditional import netcat
from nmap import nmap
from src.docker_custom import CustomClient
from src.abstract import Module
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

"""
Summary

client.compose.build(services=[service])
│
└── docker compose build
    ├── reads  cache_from: type=gha,scope=pg-static-build-x86_64  ← GHA cache hit/miss
    ├── builds image layers (only what's not cached)
    └── writes cache_to:  type=gha,mode=max,scope=pg-static-build-x86_64  ← populates cache

client.compose.up(services=[service])
│
└── docker compose up
    └── runs the container → compiles PostgreSQL → writes binaries to ./bins/<arch>/
"""
parser = argparse.ArgumentParser(description="Awesome Bins")


def check_versions(modules) -> int:
    for module in modules:
        if not module.update_version():
            print(f"failed update version for {module}, exiting")
            return -1
    return 0


def no_multi(module: Module) -> bool:
    if not module.build_x86_64():
        print(f"failed x86_64 build for {module}, exiting")
        return False

    if not module.build_x86():
        print(f"failed x86 build for {module}, exiting")
        return False

    if not module.build_arm64():
        print(f"failed arm64 build for {module}, exiting")
        return False

    if not module.build_arm32():
        print(f"failed arm32 build for {module}, exiting")
        return False

    return True


def build_module(module: Module, multi_thread: bool, arch: str | None = None):
    if not module.update_version():
        return False

    # Single arch mode (used in GHA per-runner matrix)
    if arch:
        build_fn = {
            "x86_64": module.build_x86_64,
            "x86": module.build_x86,
            "arm64": module.build_arm64,
            "arm32": module.build_arm32,
        }.get(arch)

        if build_fn is None:
            raise ValueError(f"Unsupported architecture: {arch}")

        return build_fn()

    # Local dev: all arches, optionally threaded
    builds = {
        "x86_64": module.build_x86_64,
        "x86": module.build_x86,
        "arm64": module.build_arm64,
        "arm32": module.build_arm32,
    }

    if not multi_thread:
        return all(fn() for fn in builds.values())

    with ThreadPoolExecutor(max_workers=len(builds)) as executor:
        futures = {executor.submit(fn): arch for arch, fn in builds.items()}
        for future in as_completed(futures):
            arch_name = futures[future]
            try:
                if not future.result():
                    print(f"failed {arch_name} for {module}")
                    executor.shutdown(wait=False, cancel_futures=True)
                    return False
            except Exception as ex:
                print(f"exception in {arch_name}: {ex}")
                executor.shutdown(wait=False, cancel_futures=True)
                return False
    return True


if __name__ == "__main__":
    parser.add_argument(
        "--verbose", action=argparse.BooleanOptionalAction, default=True
    )
    parser.add_argument(
        "--check-version-only",
        help="Check and update latest version of modules and exit",
        action=argparse.BooleanOptionalAction,
        default=False,
    )
    parser.add_argument(
        "--multi-thread", action=argparse.BooleanOptionalAction, default=True
    )
    parser.add_argument(
        "--single", help="Specify single module to compile", type=str, default=None
    )
    parser.add_argument(
        "--list-modules",
        help="List all available modules",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--arch",
        help="Build only a specific architecture",
        choices=["x86_64", "x86", "arm64", "arm32"],
        default=None,
    )

    args = parser.parse_args()

    all_modules = {
        "postgre": postgre.Postgre,
        "netcat_traditional": netcat.Netcat,
        "nmap": nmap.Nmap,
        "vim": vim.Vim,
    }

    if args.list_modules:
        print("Available modules:")
        for name in all_modules:
            print(f"  - {name}")
        exit(0)

    docker_client = CustomClient(verbose=args.verbose)

    if args.single:
        if args.single not in all_modules:
            print(f"[ERROR] unknown module: {args.single}")
            print(f"available modules: {', '.join(all_modules.keys())}")
            exit(-1)
        modules = [
            all_modules[args.single](verbose=args.verbose, docker_client=docker_client)
        ]
    else:
        modules = [
            cls(verbose=args.verbose, docker_client=docker_client)
            for cls in all_modules.values()
        ]

    if args.check_version_only:
        print("Checking and updating only versions files")
        status = check_versions(modules=modules)
        exit(status)

    for module in modules:
        if not build_module(module, args.multi_thread, args.arch):
            exit(-1)
