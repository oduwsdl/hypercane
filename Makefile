me_version = $(shell grep "__appversion__ = " hypercane/version.py | sed 's/__appversion__ = //g' | sed "s/'//g")

all: generic_installer rpm

source:
	-rm -rf /tmp/hypercane-source
	-rm -rf /tmp/hypercane-$(me_version)
	-rm -rf /tmp/hypercane-$(me_version).tar.gz
	mkdir /tmp/hypercane-source
	pwd
	cp -r . /tmp/hypercane-source
	-rm -rf /tmp/hypercane-source/hand-testing
	-rm -rf /tmp/hypercane-source/.vscode
	-rm -rf /tmp/hypercane-source/.git
	(cd /tmp/hypercane-source && make clean)
	mv /tmp/hypercane-source /tmp/hypercane-$(me_version)
	tar -C /tmp --exclude='.DS_Store' -c -v -z -f /tmp/hypercane-$(me_version).tar.gz hypercane-$(me_version)
	-rm -rf source-distro
	mkdir source-distro
	cp /tmp/hypercane-$(me_version).tar.gz source-distro
	
clean:
	-docker stop rpmbuild_hypercane
	-docker rm rpmbuild_hypercane
	-rm -rf .eggs
	-rm -rf eggs/
	-rm -rf build/
	-rm -rf _build/
	-rm -rf docs/build
	-rm -rf docs/source/_build
	-rm -rf dist
	-rm -rf .web_cache
	-rm -rf installer
	-rm -rf hypercane.egg-info
	-rm -rf *.log
	-rm *.sqlite
	-find . -name '*.pyc' -exec rm {} \;
	-find . -name '__pycache__' -exec rm -rf {} \;
	-rm -rf source-distro
	-rm -rf rpmbuild
	-rm -rf hypercane_with_wooey

clean-all: clean
	-rm -rf release

build-sdist: check-virtualenv
	python ./setup.py sdist

generic_installer: check-virtualenv
	./hypercane-gui/installer/linux/create-hypercane-installer.sh

rpm: source
	-rm -rf installer/rpmbuild
	mkdir -p installer/rpmbuild/RPMS installer/rpmbuild/SRPMS
	docker build -t hypercane_rpmbuild:dev -f build-rpm-Dockerfile . --build-arg hypercane_version=$(me_version) --progress=plain
	docker container run --name rpmbuild_hypercane --rm -it -v $(CURDIR)/installer/rpmbuild/RPMS:/root/rpmbuild/RPMS -v $(CURDIR)/installer/rpmbuild/SRPMS:/root/rpmbuild/SRPMS hypercane_rpmbuild:dev
	-docker stop rpmbuild_hypercane
	-docker rm rpmbuild_hypercane
	@echo "an RPM structure exists in the installer/rpmbuild directory"

deb: generic_installer
	-rm -rf installer/debbuild
	mkdir -p installer/debbuild
	docker build -t hypercane_debbuild:dev -f build-deb-Dockerfile . --build-arg hypercane_version=$(me_version) --progress=plain
	docker container run --name deb_hypercane --rm -it -v $(CURDIR)/installer/debbuild:/buildapp/debbuild hypercane_debbuild:dev
	-docker stop deb_hypercane
	-docker rm deb_hypercane
	@echo "a DEB exists in the installer/debbuild directory"

release: source build-sdist generic_installer rpm
	-rm -rf release
	-mkdir release
	cp ./installer/generic-unix/install-hypercane.sh release/install-hypercane-${me_version}.sh
	cp ./source-distro/hypercane-${me_version}.tar.gz release/
	cp ./installer/rpmbuild/RPMS/x86_64/hypercane-${me_version}-1.el8.x86_64.rpm release/
	cp ./installer/rpmbuild/SRPMS/hypercane-${me_version}-1.el8.src.rpm release/
#	cp ./installer/debbuild/hypercane-${me_version}.deb release/

check-virtualenv:
ifndef VIRTUAL_ENV
	$(error VIRTUAL_ENV is undefined, please establish a virtualenv before building)
endif

clean-virtualenv: check-virtualenv
	-pip uninstall -y hypercane
	@for p in $(shell pip freeze | awk -F== '{ print $$1 }'); do \
		pip uninstall -y $$p ; \
	done
	@echo "done removing all packages from virtualenv"
