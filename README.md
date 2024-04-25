# anybin2wheel

Package any executable to be distributed as a wheel.

As long as a license permits that, we may want to redistribute some executables
as Python wheels (e. g. from your private Python package index server).

## Usage

Given a `./something` binary, its version `1.0.0`, to package it as
`something-binary==1.0.0+yourcompanyname.1` for `macosx_12_0_arm64`:

```sh
anybin2wheel ./something something-binary 1.0.0+yourcompanyname.1 --plat-name macosx_12_0_arm64
```

More metadata can be added:

```sh
anybin2wheel ./something something-binary 1.0.0+yourcompanyname.1 --plat-name macosx_12_0_arm64 \
    --description-file DESCRIPTION.md \
    --home-page="https://vcs.yourcompanyname.local/.../something-binary" \
    --maintainer="Your Name" \
    --maintainer-email="your.email@yourcompanyname.local"
```

The choice of `--plat–name` is completely up to the user, as the executable may
be compatible with arbitrary set of platforms, specific to each individual case.
For example, some binaries may work for any `linux_x86_64`, so this platform may
be chosen instead of too fine-grained options like `manylinux*` or `musllinux*`.
