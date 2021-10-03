Name:           buttermanager
Version:        2.4.3
Release:        0%{?dist}
Summary:        Tool for managing Btrfs snapshots, balancing filesystems and more

License:        GPLv3
URL:            https://github.com/egara/buttermanager
Source0:        %{url}/archive/%{version}/%{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3dist(setuptools)
Requires:       btrfs-progs
Recommends:     grub2-btrfs

%description
ButterManager is a BTRFS tool for managing snapshots, balancing filesystems
and upgrading the system safely.

%prep
%autosetup -p1


%build
%py3_build


%install
%py3_install

install -Dpm 644 packaging/%{name}.desktop %{buildroot}%{_datadir}/applications/%{name}.desktop
install -Dpm 644 packaging/%{name}.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/%{name}.svg

# Fix the desktop file
sed -e "s/^Exec=.*/Exec=%{name}/" \
    -e "/^Path=.*/d" \
    -e "s/Icon=.*/Icon=%{name}/" \
    -i %{buildroot}%{_datadir}/applications/%{name}.desktop


%files
%license LICENSE
%doc README.md doc
%{_bindir}/buttermanager
%{python3_sitelib}/buttermanager*
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/scalable/%{name}.svg

%changelog
* TODO Sat July 3 2021 Eloy García Almadén <eloy.garcia.pca@gmail.com> - 2.4.2-0
- New release 2.4.3

* Sat July 3 2021 Eloy García Almadén <eloy.garcia.pca@gmail.com> - 2.4.2-0
- New release 2.4.2

* Sat May 1 2021 Eloy García Almadén <eloy.garcia.pca@gmail.com> - 2.4.1-0
- New release 2.4.1

* Mon Mar 31 2021 Eloy García Almadén <eloy.garcia.pca@gmail.com> - 2.4-0
- New release 2.4

* Mon Feb 15 2021 Neal Gompa <ngompa13@gmail.com> - 2.3-0
- New release 2.3

* Wed Dec 30 2020 Neal Gompa <ngompa13@gmail.com> - 2.2-0
- New release 2.2

* Wed Jun 17 2020 Neal Gompa <ngompa13@gmail.com> - 1.9-0
- Initial package
