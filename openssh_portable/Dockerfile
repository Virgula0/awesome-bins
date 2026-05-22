FROM alpine:3.21 AS zlib-builder
ARG ZLIB_VERSION=1.3.2
ARG TARGETARCH

RUN --mount=type=cache,id=apk-zlib,target=/var/cache/apk \
    apk add --no-cache build-base wget ccache

WORKDIR /build
# Download in a separate layer — if make fails, no re-download
RUN wget https://zlib.net/zlib-${ZLIB_VERSION}.tar.gz \
    && tar xzf zlib-${ZLIB_VERSION}.tar.gz

RUN --mount=type=cache,id=ccache-zlib-${TARGETARCH},target=/root/.ccache \
    export PATH="/usr/lib/ccache/bin:$PATH" && \
    export CCACHE_DIR=/root/.ccache && \
    cd zlib-${ZLIB_VERSION} && \
    ./configure --prefix=/opt/zlib-static --static && \
    make -j$(nproc) CC="ccache gcc" && \
    make install


FROM alpine:3.21 AS openssl-builder
ARG OPENSSL_VERSION=3.4.1
ARG TARGETARCH
ARG TARGETVARIANT

RUN --mount=type=cache,id=apk-openssl,target=/var/cache/apk \
    apk add --no-cache build-base wget perl linux-headers ccache

# Map BuildKit arch names → OpenSSL Configure target strings
# uname -m is unreliable for cross-compiled platforms (i686, armv7l etc.)
RUN case "${TARGETARCH}-${TARGETVARIANT}" in \
        amd64-)    echo "linux-x86_64"   ;; \
        386-)      echo "linux-x86"      ;; \
        arm64-)    echo "linux-aarch64"  ;; \
        arm-v7)    echo "linux-generic32";; \
        arm-v6)    echo "linux-generic32";; \
        *)         echo "linux-generic64";; \
    esac > /openssl_target

WORKDIR /build
RUN wget https://www.openssl.org/source/openssl-${OPENSSL_VERSION}.tar.gz \
    && tar xzf openssl-${OPENSSL_VERSION}.tar.gz

RUN --mount=type=cache,id=ccache-openssl-${TARGETARCH},target=/root/.ccache \
    export PATH="/usr/lib/ccache/bin:$PATH" && \
    export CCACHE_DIR=/root/.ccache && \
    OPENSSL_TARGET=$(cat /openssl_target) && \
    cd openssl-${OPENSSL_VERSION} && \
    ./Configure no-shared \
        --prefix=/opt/openssl-static \
        --libdir=lib \
        "${OPENSSL_TARGET}" \
        CC="ccache gcc" && \
    make -j$(nproc) && \
    make install_sw

RUN test -f /opt/openssl-static/lib/libcrypto.a


FROM alpine:3.21 AS builder
ARG TARGETARCH
ARG OPENSSH_VERSION

RUN --mount=type=cache,id=apk-openssh,target=/var/cache/apk \
    apk add --no-cache \
    build-base wget autoconf automake linux-headers ccache

COPY --from=zlib-builder   /opt/zlib-static   /opt/zlib-static
COPY --from=openssl-builder /opt/openssl-static /opt/openssl-static

WORKDIR /build
RUN wget https://cdn.openbsd.org/pub/OpenBSD/OpenSSH/portable/openssh-${OPENSSH_VERSION}.tar.gz \
    && tar xzf openssh-${OPENSSH_VERSION}.tar.gz

WORKDIR /build/openssh-${OPENSSH_VERSION}
RUN --mount=type=cache,id=ccache-openssh-${TARGETARCH},target=/root/.ccache \
    export PATH="/usr/lib/ccache/bin:$PATH" && \
    export CCACHE_DIR=/root/.ccache && \
    autoreconf && \
    ./configure \
        --prefix=/opt/openssh-static \
        --sysconfdir=/etc/ssh \
        --with-privsep-user=nobody \
        --with-privsep-path=/var/empty \
        --with-ssl-engine \
        --with-zlib=/opt/zlib-static \
        --with-ssl-dir=/opt/openssl-static \
        CFLAGS="-I/opt/zlib-static/include -I/opt/openssl-static/include -O2" \
        LDFLAGS="-L/opt/zlib-static/lib -L/opt/openssl-static/lib -static -no-pie" \
        LIBS="-lz -lcrypto" \
        CC="ccache gcc" && \
    make -j$(nproc) && \
    make install-nosysconf && \
    echo "=== Static binary check ===" && \
    for bin in /opt/openssh-static/bin/* /opt/openssh-static/sbin/*; do \
        [ -f "$bin" ] || continue; \
        printf "%s: " "$(basename "$bin")"; \
        file "$bin" | grep -q "statically linked" \
            && echo "OK (static)" \
            || { echo "FAILED (not static) - $bin"; exit 1; }; \
    done


FROM alpine:3.21
ARG HOST_UID=1000
ARG HOST_GID=1000

RUN addgroup -g "$HOST_GID" sshuser 2>/dev/null || true \
    && adduser -D -u "$HOST_UID" -G sshuser sshuser 2>/dev/null || true

COPY --from=builder /opt/openssh-static/ /usr/local/
RUN chmod 755 /usr/local/bin/* /usr/local/sbin/* 2>/dev/null || true

USER sshuser
CMD ["sh", "-c", "mkdir -p /output && \
    cp /usr/local/bin/ssh \
       /usr/local/bin/scp \
       /usr/local/bin/sftp \
       /usr/local/bin/ssh-keygen \
       /usr/local/sbin/sshd \
       /output/ 2>/dev/null && \
    chmod 755 /output/*"]