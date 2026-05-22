FROM alpine:3.21 AS builder

ARG VIM_VERSION=9.2.0499

RUN apk add --no-cache \
    build-base \
    wget \
    tar \
    ncurses-static \
    musl-dev \
    automake \
    linux-headers \
    perl

WORKDIR /build

RUN wget https://github.com/vim/vim/archive/refs/tags/v${VIM_VERSION}.tar.gz -O vim-${VIM_VERSION}.tar.gz \
    && tar xzf vim-${VIM_VERSION}.tar.gz \
    && cd vim-${VIM_VERSION} \
    && cp "$(automake --print-libdir)/config.guess" src/auto/ \
    && cp "$(automake --print-libdir)/config.sub" src/auto/ \
    && ./configure \
        --prefix=/opt/vim-static \
        --disable-shared \
        --enable-static \
        --with-tlib=ncurses \
        --disable-gui \
        --without-x \
        --disable-nls \
        --disable-selinux \
        --disable-canberra \
        --disable-libsodium \
        --disable-acl \
        --disable-gpm \
        --disable-channel \
        --disable-netbeans \
        --disable-cscope \
        --disable-perlinterp \
        --disable-pythoninterp \
        --disable-python3interp \
        --disable-rubyinterp \
        --disable-luainterp \
        --disable-mzschemeinterp \
        --disable-tclinterp \
        CFLAGS='-O2 -static' \
        LDFLAGS='-static -no-pie' \
    && make -j"$(nproc)" \
    && make install \
    && echo "=== Installed files in /opt/vim-static ===" \
    && ls -la /opt/vim-static/bin/ || true \
    && ( test -f /opt/vim-static/bin/vim || cp src/vim /opt/vim-static/bin/vim ) \
    && strip /opt/vim-static/bin/vim \
    && echo "=== Static binary check ===" \
    && file /opt/vim-static/bin/vim | grep -q "statically linked" \
    && echo "OK (static)" \
    || { echo "FAILED (not static) - $(file /opt/vim-static/bin/vim)"; exit 1; }


FROM alpine:3.21

ARG HOST_UID=1000
ARG HOST_GID=1000

RUN addgroup -g "$HOST_GID" vimuser 2>/dev/null || true \
    && adduser -D -u "$HOST_UID" -G vimuser vimuser 2>/dev/null || true

COPY --from=builder /opt/vim-static/bin/ /vim-bins/

RUN chmod -R 755 /vim-bins/

USER vimuser

CMD ["sh", "-c", "mkdir -p /output && cp -r /vim-bins/. /output/ && chmod -R 755 /output"]