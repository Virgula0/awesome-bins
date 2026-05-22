# awesome-bins

Useful static binaries for pentesting or IT stuff updated weekly for x86_64, x86, ARM64, ARM32

[![Release Action](https://github.com/Virgula0/awesome-bins/actions/workflows/release.yaml/badge.svg)](https://github.com/Virgula0/awesome-bins/actions/workflows/release.yaml)
[![GitHub Release](https://img.shields.io/github/v/release/Virgula0/awesome-bins)](https://github.com/Virgula0/awesome-bins/releases)

> [!WARNING]
> This repo is experimental. It tries to release updated static binaries automatically, but compilation directives change a lot between
> different versions. Also, the push releases are experimental, and it depends on how much time compilations need. The best way is to
> run the script locally (see the run section), otherwise rely on GitHub releases (release section)

# Supported OS

Only Linux binaries are supported at the moment, maybe in future I'll consider `Windows` and `MacOS` too.

# List of compiled projects (each one including all archs)

- [NMAP and all suite](./nmap)
- [TCPDUMP](./tcpdump)
- [PSQL, PG_DUMP, PG_DUMPALL](./postgre)
- [NETCAT_TRADITIONAL](./netcat_traditional)
- [VIM](./vim)
- [OPENSSH suite](./openssh_portable)
- [Python3](./python3)
- [GCC](./gcc)
- [TMUX](./tmux)
- [MariaDB](./mariadb)

# PRs

Pull requests are welcome, but be sure to follow the same pattern as the existing modules.
For more info refer to [PR.md](PR.md)

# Releases

You can just check for binaries here: [https://github.com/Virgula0/awesome-bins/releases](https://github.com/Virgula0/awesome-bins/releases)

# Compile binaries locally

## Pre-requisites

General use

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

You need `docker-buildx` to run cross-platform compilation options (especially for `arm` devices)
Install via `apt` or whatever package manager is available.

```bash
sudo apt update
sudo apt install docker-buildx -y
```

```bash
sudo pacman -Syu docker-buildx
```

```bash
dnf install docker-buildx
```

Once installed, run the cross-platform container (only once required unless you reboot the host)

```bash
make setup-docker
```

## Basic usage

```bash
python3 main.py --help
usage: main.py [-h] [--verbose | --no-verbose] [--check-version-only | --no-check-version-only] [--multi-thread | --no-multi-thread] [--single SINGLE] [--list-modules] [--arch {x86_64,x86,arm64,arm32}]

Awesome Bins

options:
  -h, --help            show this help message and exit
  --verbose, --no-verbose
  --check-version-only, --no-check-version-only
                        Check and update latest version of modules and exit
  --multi-thread, --no-multi-thread
  --single SINGLE       Specify single module to compile
  --list-modules        List all available modules
  --arch {x86_64,x86,arm64,arm32}
                        Build only a specific architecture
```

### List modules

Each of the programs compiled here is a module. The option shows all modules.

```bash
python3 main.py --list-modules
Available modules:
  - postgre
  - netcat_traditional
  - nmap
  - vim
  - tcpdump
  - openssh_portable
  - python3
  - gcc
  - tmux
  - mariadb
```

### Update latest versions

Update the latest versions only. By default, when compiling containers, the script automatically updates to the latest versions
in `**/lts_version`, but you may want to update only versions and exit without actually building something.
It is advisable not to change `**/stable_working_version` as these versions are used by the script as fallback versions whenever the
build of `lts_version` fails. This is needed because managing different versions of compilation is kinda challenging, and even a small variation
can disrupt the builds. Remember that most of the compiled binaries contain a modified `Makefile` to allow static compilations of the same.

```bash
python3 main.py --check-version-only
```

## Clean before starting

Each time, it is advisable to clean old compilations with

```bash
make clean-bins
```

## Compile a single module

This is useful if you're interested in compiling a single module.

```bash
python3 main.py --single postgre
```

Only `postgre` binaries will be compiled; you can see them at the end with `make check-bins`.

## Compile single architecture for a single module

Example for `arm64`

```bash
python3 main.py --single netcat_traditional --arch arm64
```

## Compile all modules (single-thread)

Run build containers one at a time:

```bash
python3 main.py --no-multi-thread
```

By default, the script runs in `multi-thread` mode.
You can find builds in `make check-bins`

## Compile all modules (multi-thread)

By default, the script runs more containers in parallel at a time, which can be very resource-intensive:

```bash
python3 main.py
```