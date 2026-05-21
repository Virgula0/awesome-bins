FROM alpine:3.19 AS builder
ARG PYTHON3_VERSION
ARG TARGETARCH

RUN apk add --no-cache \
    build-base \
    wget \
    xz \
    gcc \
    linux-headers \
    ccache \
    libc6-compat \
    musl-dev \
    openssl-dev

WORKDIR /build
RUN wget https://www.python.org/ftp/python/${PYTHON3_VERSION}/Python-${PYTHON3_VERSION}.tar.xz \
    && tar -xf Python-${PYTHON3_VERSION}.tar.xz \
    && mv Python-${PYTHON3_VERSION} python-source

WORKDIR /build/python-source

RUN --mount=type=cache,id=ccache-python-${TARGETARCH},target=/root/.ccache \
    export PATH="/usr/lib/ccache/bin:$PATH" \
    && export CCACHE_DIR=/root/.ccache \
    && ./configure \
        --prefix=/opt/python-static \
        --disable-shared \
        --enable-optimizations \
        CFLAGS="-Os -static" \
        CPPFLAGS="-static" \
        LDFLAGS="-static -no-pie" \
    && make -j$(nproc) \
    && make install

RUN /opt/python-static/bin/python3 -m ensurepip \
    && /opt/python-static/bin/python3 -m pip install --upgrade pip

RUN for bin in /opt/python-static/bin/*; do \
        [ -f "$bin" ] || continue; \
        printf "%s: " "$(basename "$bin")"; \
        file "$bin" | grep -q "statically linked" \
            && echo "OK (static)" \
            || { echo "FAILED (not static) - $bin"; exit 1; }; \
    done

FROM alpine:3.19
ARG HOST_UID=1000
ARG HOST_GID=1000

RUN addgroup -g "$HOST_GID" pyuser 2>/dev/null || true \
    && adduser -D -u "$HOST_UID" -G pyuser pyuser 2>/dev/null || true

COPY --from=builder /opt/python-static /python-static

RUN chmod -R 755 /python-static

USER pyuser

CMD ["sh", "-c", "mkdir -p /output && cp -r /python-static /output/ && chmod -R 755 /output/python-static"]