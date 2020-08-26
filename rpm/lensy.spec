%global appname Lensy
%global uuid    com.github.amikha1lov.%{appname}

%global commit  47a4b79fbcc29f4108045ccf47993127ffc04d30
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global date    20200824

Name:           lensy
Version:        0
Release:        1.%{date}git%{shortcommit}%{?dist}
Summary:        FIXME
BuildArch:      noarch

License:        GPLv3+
URL:            https://github.com/amikha1lov/Lensy
%dnl Source0:        %{url}/archive/%{commit}/%{name}-%{version}.%{date}git%{shortcommit}.tar.gz
Source0:        %{url}/archive/%{commit}/%{appname}-trash.zip

BuildRequires:  desktop-file-utils
BuildRequires:  intltool
BuildRequires:  libappstream-glib
BuildRequires:  meson >= 0.50.0
BuildRequires:  python3-devel
BuildRequires:  pkgconfig(glib-2.0)

Requires:       gtk3
Requires:       hicolor-icon-theme
Requires:       python3-pydbus
Requires:       slop

%description
FIXME.


%prep
%autosetup -n %{appname}-trash -p1


%build
%meson
%meson_build


%install
%meson_install
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
* Wed Aug 26 20:41:17 EEST 2020 Artem Polishchuk <ego.cordatus@gmail.com> - 0-1.20200824git47a4b79
- Initial package
