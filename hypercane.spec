Name: hypercane
Version: {{ hypercane_version }}
Summary: Hypercane is a framework of algorithms for sampling mementos from a web archive collection.
Release: 1%{?dist}
License: MIT
Source0: %{name}-%{version}.tar.gz
ExclusiveArch: x86_64

BuildRequires: coreutils, sed, grep, tar, mktemp, python3-virtualenv, python38, gcc
Requires: python38, postgresql, libjpeg-turbo, zlib, libtiff, freetype-devel, freetype, lcms2, libwebp, tcl, tk, openjpeg2, fribidi, harfbuzz, libxcb, cairo
Requires(pre): shadow-utils, python38
AutoReq: no

%description
Hypercane is a framework for building algorithms for sampling mementos from a web archive collection. Hypercane is the entry point of the Dark and Stormy Archives (DSA) toolkit. A user can generate samples with Hypercane and then view those samples via the Web Archive Storytelling tool Raintale, thus allowing the user to automatically summarize a web archive collection as a few small samples visualized as a social media story.

%define  debug_package %{nil}
%define _build_id_links none
%global _enable_debug_package 0
%global _enable_debug_package ${nil}
%global __os_install_post /usr/lib/rpm/brp-compress %{nil}

%prep
%setup -q

%build
rm -rf $RPM_BUILD_ROOT
export VIRTUAL_ENV=system
make generic_installer

# thanks -- https://fedoraproject.org/wiki/Packaging%3aUsersAndGroups
%pre
getent group dsa >/dev/null || groupadd -r dsa
getent passwd hypercane >/dev/null || \
    useradd -r -g dsa -d /opt/hypercane -s /sbin/nologin \
    -c "hypercane service account" hypercane
exit 0

%install
echo RPM_BUILD_ROOT is $RPM_BUILD_ROOT
mkdir -p ${RPM_BUILD_ROOT}/opt/hypercane
mkdir -p ${RPM_BUILD_ROOT}/etc/systemd/system
mkdir -p ${RPM_BUILD_ROOT}/usr/bin
bash ./installer/generic-unix/install-hypercane.sh -- --install-directory ${RPM_BUILD_ROOT}/opt/hypercane --install-all --python-exe /usr/bin/python --skip-script-install --hypercane-user hypercane --cli-wrapper-path ${RPM_BUILD_ROOT}/usr/bin/ --mongodb-url mongodb://127.0.0.1:27017/hypercane_cache_storage
# TODO: fix this, everything should stay in RPM_BUILD_ROOT
mv /etc/systemd/system/hypercane-celery.service ${RPM_BUILD_ROOT}/etc/systemd/system/hypercane-celery.service
mv /etc/systemd/system/hypercane-django.service ${RPM_BUILD_ROOT}/etc/systemd/system/hypercane-django.service
find ${RPM_BUILD_ROOT}/opt/hypercane/hypercane-virtualenv/bin -type f -exec sed -i "s?${RPM_BUILD_ROOT}??g" {} \;
echo 'HC_CACHE_STORAGE=mongodb://127.0.0.1:27017/hypercane_cache_storage' > ${RPM_BUILD_ROOT}/etc/hypercane.conf
sed -i "s?${RPM_BUILD_ROOT}??g" ${RPM_BUILD_ROOT}/etc/systemd/system/hypercane-django.service
sed -i "s?${RPM_BUILD_ROOT}??g" ${RPM_BUILD_ROOT}/etc/systemd/system/hypercane-celery.service
sed -i "s?${RPM_BUILD_ROOT}??g" ${RPM_BUILD_ROOT}/usr/bin/hc
sed -i 's?\(python ${WOOEY_DIR}/manage.py addscript "${SCRIPT_DIR}/scripts/Create Video Story.py"\)?#\1?g'  ${RPM_BUILD_ROOT}/opt/hypercane/hypercane-gui/add-hypercane-scripts.sh
sed -i "s?^python ?/opt/hypercane/hypercane-virtualenv/bin/python ?g" ${RPM_BUILD_ROOT}/opt/hypercane/hypercane-gui/add-hypercane-scripts.sh
sed -i "s?^python ?/opt/hypercane/hypercane-virtualenv/bin/python ?g" ${RPM_BUILD_ROOT}/opt/hypercane/hypercane-gui/set-hypercane-database.sh


%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-, hypercane, dsa, 0755)
/opt/hypercane/
%attr(0644, hypercane, dsa) %config(noreplace) /etc/hypercane.conf
%attr(0755, root, root) /etc/systemd/system/hypercane-django.service
%attr(0755, root, root) /etc/systemd/system/hypercane-celery.service
%attr(0755, hypercane, dsa) /usr/bin/hc

%post
su -l hypercane -s /bin/bash /opt/hypercane/hypercane-gui/add-hypercane-scripts.sh
/usr/bin/systemctl enable hypercane-celery.service
/usr/bin/systemctl enable hypercane-django.service
# download NLTK data
su -l hypercane -s /bin/bash -c '/opt/hypercane/hypercane-virtualenv/bin/python -m nltk.downloader stopwords'
su -l hypercane -s /bin/bash -c '/opt/hypercane/hypercane-virtualenv/bin/python -m nltk.downloader punkt'
su -l hypercane -s /bin/bash -c '/opt/hypercane/hypercane-virtualenv/bin/python -m spacy download en_core_web_sm'

%preun
/usr/bin/systemctl stop hypercane-django.service
/usr/bin/systemctl stop hypercane-celery.service
/usr/bin/systemctl disable hypercane-django.service
/usr/bin/systemctl disable hypercane-celery.service

%postun
/usr/sbin/userdel hypercane
find /opt/hypercane -name __pycache__ -exec rm -rf {} \;
find /opt/hypercane -name celerybeat-schedule -exec rm -rf {} \;
if [ -d /opt/hypercane/hypercane_with_wooey/hypercane_with_wooey/user_uploads ]; then
    tar -C /opt/hypercane/hypercane_with_wooey/hypercane_with_wooey -c -v -z -f /opt/hypercane/user_uploads-backup-`date '+%Y%m%d%H%M%S'`.tar.gz user_uploads
    rm -rf /opt/hypercane/hypercane_with_wooey
fi
