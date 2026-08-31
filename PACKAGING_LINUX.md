# Native Linux packages — Registros Clínicos by CodeCafe

## Goal
The end-user should receive one native installer file and never need the source tree.

- Debian / Ubuntu / Linux Mint: `.deb`
- Fedora / RHEL / CentOS Stream / Rocky / AlmaLinux: `.rpm`

The package installs the application under `/opt/codecafe-lab-records`, a launcher under
`/usr/bin/codecafe-lab-records`, and a desktop-menu entry. Clinical data remains in the
user's data directory and is not part of the package.

## Important compatibility rule
Build the DEB on a Debian/Ubuntu-family machine and the RPM on an RPM-family machine.
The PyInstaller payload is a native Linux binary and should not be treated as a universal
Linux binary across distributions with different system libraries.

## Build a DEB
On Debian/Ubuntu-family Linux:

```bash
./build_deb.sh
```

Result:

```text
dist/packages/codecafe-lab-records_0.6.8_<arch>.deb
```

Install for testing:

```bash
sudo apt install ./dist/packages/codecafe-lab-records_0.6.8_amd64.deb
```

For a normal end user, double-clicking the `.deb` should open the distribution's graphical
package installer/software center.

## Build an RPM
Install the RPM build tool once, for example on CentOS Stream/Fedora-family systems:

```bash
sudo dnf install rpm-build
```

Then:

```bash
./build_rpm.sh
```

The RPM is written to `dist/packages/`.

Install for testing:

```bash
sudo dnf install ./dist/packages/codecafe-lab-records-*.rpm
```

## Auto-detect

```bash
./build_native_package.sh
```

This builds the package type native to the current distribution family.

## Reuse an already compiled payload
If `dist/codecafe-lab-records/` was already built **on the same OS family and architecture**:

```bash
./build_deb.sh --reuse-build
# or
./build_rpm.sh --reuse-build
```

Do not use `--reuse-build` to wrap a CentOS-built PyInstaller binary in a DEB or vice versa.


## v0.6.9 safe RPM staging

The standalone Linux build under `dist/codecafe-lab-records/` is treated as immutable during native package creation. The RPM builder copies that known-good payload to `build/rpm-staging/` and performs any RPM-family compatibility adjustment only in that staging copy. In particular, the optional Qt TIFF image-format plugin may be omitted from the RPM staging payload on EL10 when it introduces an unavailable `libtiff.so.5` ABI dependency. The original standalone build and DEB payload are not modified by this RPM-specific step.
