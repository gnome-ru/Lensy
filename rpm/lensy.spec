%global appname Lensy
%global uuid com.github.amikha1lov.%{appname}

%define build_timestamp %{lua: print(os.date("%Y%m%d"))}

Name: lensy
Version: 0
Release: 0.4.%{build_timestamp}%{?dist}
Summary: FIXME
BuildArch: noarch

License: GPLv3+
URL: https://github.com/amikha1lov/Lensy
%dnl Source0: %{url}/archive/%{commit}/%{name}-%{version}-%{build_timestamp}.tar.gz
Source0: %{url}/archive/%{commit}/%{appname}-trash.zip

BuildRequires: desktop-file-utils
BuildRequires: intltool
BuildRequires: libappstream-glib
BuildRequires: meson >= 0.50.0
BuildRequires: python3-devel
BuildRequires: pkgconfig(glib-2.0)

Requires: gtk3
Requires: hicolor-icon-theme
Requires: python3-pydbus
Requires: slop

%description
FIXME.


%prep
%autosetup -n %{appname}-trash -p1


%build
%meson
%meson_build


%install
%meson_install
%py_byte_compile %{python3} %{buildroot}%{_datadir}/%{name}/%{name}/
%dnl %find_lang %{uuid}


%check
%dnl appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/*.xml
desktop-file-validate %{buildroot}%{_datadir}/applications/*.desktop


%dnl %files -f %{uuid}.lang
%files
%license COPYING
%dnl %doc README.md CREDITS
%{_bindir}/%{name}
%{_datadir}/%{name}/
%{_datadir}/applications/*.desktop
%{_datadir}/glib-2.0/schemas/*.gschema.xml
%dnl %{_datadir}/icons/hicolor/*/*/*.png
%{_datadir}/appdata/*.xml
%dnl %{_metainfodir}/*.xml


%changelog
* Sat Aug 29 2020 Artem Polishchuk <ego.cordatus@gmail.com> - 0-3.20200829git348c55d
- Update to latest git snapshot

* Fri Aug 28 01:48:46 EEST 2020 Artem Polishchuk <ego.cordatus@gmail.com> - 0-2.20200828git9949647
- Update to latest git snapshot

* Wed Aug 26 20:41:17 EEST 2020 Artem Polishchuk <ego.cordatus@gmail.com> - 0-1.20200824git47a4b79
- Initial package
