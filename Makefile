install-requirements:
	pip install requirements.txt
.PHONY: install-requirements

# sudo pacman -S docker-buildx
setup-docker:
	docker run --privileged --rm tonistiigi/binfmt --install all
	docker buildx create --use --name multiarch
	docker buildx inspect --bootstrap
.PHONY: setup-docker

clean-bins:
	rm **/bins/**/* 2> /dev/null
.PHONY: clean-bins