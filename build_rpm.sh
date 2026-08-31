#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")"

APP_ID="codecafe-lab-records"
PKG_VERSION="${CODECAFE_PACKAGE_VERSION:-0.6.11}"
RELEASE="${CODECAFE_RPM_RELEASE:-1}"

usage() {
  cat <<USAGE
Usage: ./build_rpm.sh [--reuse-build]

Builds a native .rpm for Fedora/RHEL/CentOS/Rocky/Alma-family Linux systems.
By default it first runs ./build_linux.sh. Use --reuse-build only when
./dist/codecafe-lab-records already contains a build created on THIS RPM-family
system and architecture.
USAGE
}
REUSE=0
case "${1:-}" in
  "") ;;
  --reuse-build) REUSE=1 ;;
  -h|--help) usage; exit 0 ;;
  *) usage >&2; exit 64 ;;
esac

[[ "$(uname -s)" == "Linux" ]] || { echo "RPM packages must be built on Linux." >&2; exit 69; }
if [[ -r /etc/os-release ]]; then
  . /etc/os-release
  family=" ${ID:-} ${ID_LIKE:-} "
  if [[ "$family" != *" fedora "* && "$family" != *" rhel "* && "$family" != *" centos "* ]]; then
    echo "Refusing to build an RPM from a non-RPM-family host (${PRETTY_NAME:-unknown})." >&2
    echo "Build the RPM on Fedora/RHEL/CentOS/Rocky/Alma so the bundled Linux binary targets that family." >&2
    exit 65
  fi
fi
command -v rpmbuild >/dev/null 2>&1 || {
  echo "rpmbuild is required. On CentOS/Fedora/RHEL-family systems install the rpm-build package." >&2
  exit 69
}

if (( ! REUSE )); then
  ./build_linux.sh
fi
APP_DIR="dist/$APP_ID"
[[ -x "$APP_DIR/$APP_ID" ]] || { echo "Missing Linux build: $APP_DIR/$APP_ID" >&2; exit 70; }

TOP="$PWD/build/rpmbuild"
ROOT="$PWD/build/rpm-root"
STAGING="$PWD/build/rpm-staging/$APP_ID"
rm -rf "$TOP" "$ROOT" "$PWD/build/rpm-staging"
mkdir -p "$TOP"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS} \
  "$ROOT/opt/$APP_ID" \
  "$ROOT/usr/bin" \
  "$ROOT/usr/share/applications" \
  "$ROOT/usr/share/icons/hicolor/scalable/apps" \
  "$ROOT/usr/share/doc/$APP_ID" \
  "$STAGING"

echo "Creating RPM staging copy; original Linux build will not be modified."
cp -a "$APP_DIR/." "$STAGING/"

# CentOS Stream 10 exposes libtiff.so.6, while some PyQt6 wheels may ship an
# optional Qt TIFF image-format plugin linked against libtiff.so.5. CodeCafe's
# clinical PDF/image handling uses PyMuPDF rather than Qt's TIFF plugin. Remove
# that plugin ONLY from the RPM staging copy. The known-good standalone build in
# dist/codecafe-lab-records remains untouched for regression/fallback testing.
QT_TIFF_PLUGIN="$STAGING/_internal/PyQt6/Qt6/plugins/imageformats/libqtiff.so"
if [[ -e "$QT_TIFF_PLUGIN" ]]; then
  echo "RPM staging only: removing optional Qt TIFF plugin: $QT_TIFF_PLUGIN"
  rm -f "$QT_TIFF_PLUGIN"
fi

# Prove the original payload was not changed by the staging operation.
if [[ -e "$APP_DIR/_internal/PyQt6/Qt6/plugins/imageformats/libqtiff.so" ]]; then
  echo "Original build preserved: Qt TIFF plugin still exists in $APP_DIR"
fi

cp -a "$STAGING/." "$ROOT/opt/$APP_ID/"
cp AUTHORSHIP.md "$ROOT/usr/share/doc/$APP_ID/AUTHORSHIP.md"
[[ -f README.md ]] && cp README.md "$ROOT/usr/share/doc/$APP_ID/README.md"

cat > "$ROOT/usr/bin/$APP_ID" <<'WRAPPER'
#!/usr/bin/env bash
exec /opt/codecafe-lab-records/codecafe-lab-records "$@"
WRAPPER
chmod 755 "$ROOT/usr/bin/$APP_ID"

cat > "$ROOT/usr/share/applications/$APP_ID.desktop" <<'DESKTOP'
[Desktop Entry]
Type=Application
Version=1.0
Name=Clinical Records
Name[es]=Registros Clínicos
Comment=Clinical laboratory records organizer
Comment[es]=Organizador de análisis y registros clínicos
Exec=/usr/bin/codecafe-lab-records
Icon=codecafe-lab-records
Terminal=false
Categories=Office;Science;Utility;
StartupNotify=true
DESKTOP

cat > "$ROOT/usr/share/icons/hicolor/scalable/apps/$APP_ID.svg" <<'SVG'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128">
  <rect x="8" y="8" width="112" height="112" rx="26" fill="#2557a7"/>
  <path d="M39 35h50v11H39zm0 23h50v11H39zm0 23h32v11H39z" fill="white"/>
  <circle cx="91" cy="87" r="18" fill="#ffffff" opacity=".96"/>
  <path d="M91 76v22M80 87h22" stroke="#2557a7" stroke-width="7" stroke-linecap="round"/>
</svg>
SVG

( cd "$ROOT" && tar -czf "$TOP/SOURCES/${APP_ID}-root.tar.gz" . )

cat > "$TOP/SPECS/$APP_ID.spec" <<SPEC
%global _build_id_links none
Name:           $APP_ID
Version:        $PKG_VERSION
Release:        $RELEASE%{?dist}
Summary:        Registros Clínicos by CodeCafe
License:        Proprietary
URL:            https://codecafe.io
Source0:        %{name}-root.tar.gz

Requires:       libxcb
Requires:       libxkbcommon-x11
Requires:       mesa-libGL
Requires:       dbus-libs
Requires:       fontconfig
Recommends:     tesseract

%description
Registros Clínicos by CodeCafe organizes laboratory PDFs, structured results, trends,
daily measurements including blood pressure, glucose and weight, and related clinical
documents in an elder-friendly desktop interface. Original documents and personal clinical data are stored separately
under the user's profile and are preserved during application upgrades.

%prep

%build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}
tar -xzf %{SOURCE0} -C %{buildroot}

%post
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database /usr/share/applications >/dev/null 2>&1 || :
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor >/dev/null 2>&1 || :
fi

%postun
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database /usr/share/applications >/dev/null 2>&1 || :
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor >/dev/null 2>&1 || :
fi

%files
/opt/%{name}
/usr/bin/%{name}
/usr/share/applications/%{name}.desktop
/usr/share/icons/hicolor/scalable/apps/%{name}.svg
/usr/share/doc/%{name}

%changelog
* Sun Aug 16 2026 Jaime Sánchez Sáenz <contacto@codecafe.io> - $PKG_VERSION-$RELEASE
- RPM package uses a distro-specific staging copy; standalone build remains untouched.
SPEC

rpmbuild --define "_topdir $TOP" --define "_build_id_links none" -bb "$TOP/SPECS/$APP_ID.spec"
mkdir -p "$PWD/dist/packages"
find "$TOP/RPMS" -type f -name '*.rpm' -exec cp -f {} "$PWD/dist/packages/" \;

# PyInstaller bundles many ELF objects that can share GNU build-ids with
# system libraries. RPM must not publish global /usr/lib/.build-id links for
# this private /opt payload, or installation can conflict with system RPMs.
for rpmfile in "$PWD"/dist/packages/*.rpm; do
  if rpm -qlp "$rpmfile" | grep -q '^/usr/lib/\.build-id/'; then
    echo "ERROR: RPM unexpectedly contains /usr/lib/.build-id links." >&2
    rpm -qlp "$rpmfile" | grep '^/usr/lib/\.build-id/' | head -n 20 >&2 || true
    exit 74
  fi
done

# Validate the generated RPM against the currently enabled RPM repositories.
# This catches bundled ELF objects that accidentally require an unavailable
# ABI (such as libtiff.so.5 on CentOS Stream 10) before the package is shared.
VALIDATION_FAILED=0
while IFS= read -r rpmfile; do
  echo "Validating RPM dependencies: $rpmfile"
  if command -v dnf >/dev/null 2>&1; then
    if ! dnf -q --assumeno --disablerepo=google-chrome install "$rpmfile" >/tmp/codecafe-rpm-check.log 2>&1; then
      if grep -qE 'nothing provides|conflicting requests|Problem:' /tmp/codecafe-rpm-check.log; then
        cat /tmp/codecafe-rpm-check.log >&2
        VALIDATION_FAILED=1
      fi
    fi
  fi

  if rpm -qpR "$rpmfile" | grep -q 'libtiff\.so\.5'; then
    echo "ERROR: RPM still requires obsolete libtiff.so.5. Refusing to publish it." >&2
    rpm -qpR "$rpmfile" | grep 'libtiff\.so\.5' >&2 || true
    VALIDATION_FAILED=1
  fi
done < <(find "$PWD/dist/packages" -maxdepth 1 -type f -name '*.rpm' -print)
rm -f /tmp/codecafe-rpm-check.log
(( VALIDATION_FAILED == 0 )) || exit 73

echo
echo "RPM package(s):"
find "$PWD/dist/packages" -maxdepth 1 -type f -name '*.rpm' -print
