# CodeCafe Lab Records v0.6.9

## Safe RPM staging

- The known-good standalone Linux build is never modified by RPM packaging.
- `build_rpm.sh` copies `dist/codecafe-lab-records/` into `build/rpm-staging/`.
- The optional Qt TIFF plugin is removed only from that RPM staging copy when present, avoiding the `libtiff.so.5` dependency seen on CentOS Stream 10.
- DEB and standalone Linux payloads remain unchanged.
- RPM dependency validation still runs before the package is considered distributable.
