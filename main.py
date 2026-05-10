from postgre import postgre
from src.docker_custom import CustomClient
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

parser = argparse.ArgumentParser(description="Awesome Bins")

def check_versions(modules) -> int:
    for module in modules:
        if not module.update_version():
            print(f"failed update version for {module}, exiting")
            return -1
    return 0

if __name__ == "__main__":
    parser.add_argument("--verbose", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--check-version-only", action=argparse.BooleanOptionalAction, default=False)
    args = parser.parse_args()

    docker_client = CustomClient(verbose=args.verbose)
    modules = [
        postgre.Postgre(verbose=args.verbose, docker_client=docker_client)
    ]

    if args.check_version_only:
        print("Checking and updating only versions files")
        status = check_versions(modules=modules)
        exit(status)

    for module in modules:
        print(f"Building {module} ...")

        if not check_versions(modules=modules):
            print(f"failed update version for {module}, exiting")
            exit(-1)

        builds = {
            "x86_64": module.build_x86_64,
            "x86":    module.build_x86,
            "arm64":  module.build_arm64,
            "arm32":  module.build_arm32,
        }

        with ThreadPoolExecutor(max_workers=len(builds)) as executor:
            futures = {executor.submit(fn): arch for arch, fn in builds.items()}

            for future in as_completed(futures):
                arch = futures[future]
                if not future.result():
                    print(f"failed {arch} build for {module}, exiting")
                    exit(-1)
                print(f"{arch} build completed for {module}")