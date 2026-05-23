FROM alpine:3.21@sha256:48b0309ca019d89d40f670aa1bc06e426dc0931948452e8491e3d65087abc07d AS builder

ARG TMUX_VERSION

RUN apk add --no-cache \
    build-base \
    wget \
    autoconf \
    automake \
    libtool \
    pkgconfig \
    m4 \
    byacc \
    linux-headers \
    musl-dev \
    libevent-dev \
    libevent-static \
    ncurses-dev \
    ncurses-static

WORKDIR /build

RUN wget https://github.com/tmux/tmux/releases/download/${TMUX_VERSION}/tmux-${TMUX_VERSION}.tar.gz && \
    tar xzf tmux-${TMUX_VERSION}.tar.gz && \
    cd tmux-${TMUX_VERSION} && \
    ./configure \
        --prefix=/opt/tmux-static \
        --enable-static \
        CFLAGS='-O2' && \
    make -j$(nproc) \
        LDFLAGS="-static" && \
    make install

RUN for bin in /opt/tmux-static/bin/*; do \
        [ -f "$bin" ] || continue; \
        file "$bin" | grep -q "statically linked" || { echo "Not static: $bin"; exit 1; }; \
    done

FROM alpine:3.21@sha256:48b0309ca019d89d40f670aa1bc06e426dc0931948452e8491e3d65087abc07d

ARG HOST_UID=1000
ARG HOST_GID=1000

RUN addgroup -g "$HOST_GID" tmuxuser 2>/dev/null || true && \
    adduser -D -u "$HOST_UID" -G tmuxuser tmuxuser 2>/dev/null || true

COPY --from=builder /opt/tmux-static/bin/tmux /usr/local/bin/tmux
RUN chmod 755 /usr/local/bin/tmux

USER tmuxuser
CMD ["sh", "-c", "mkdir -p /output && cp /usr/local/bin/tmux /output/ && chmod 755 /output/tmux"]