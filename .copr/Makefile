spec := tuxedo-drivers-kmod.spec
outdir := ./

SPEC_FILENAME := $(notdir $(spec))
SOURCE := $(lastword $(shell rpmspec -P $(spec) |grep Source:))

all: clean download prepare srpm build retrieve-srpm retrieve-rpm

copr: clean download prepare srpm retrieve retrieve-srpm

prepare:
	mkdir -p rpmbuild/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
	cp $(notdir $(SOURCE)) rpmbuild/SOURCES/
	cp $(spec) rpmbuild/SPECS/

download:
	curl -OL $(SOURCE)

srpm:
	rpmbuild --define "_topdir `pwd`/rpmbuild" --undefine dist -bs rpmbuild/SPECS/$(SPEC_FILENAME)

build:
	dnf builddep -y rpmbuild/SRPMS/*.src.rpm
	rpmbuild --define "_topdir `pwd`/rpmbuild" -rb rpmbuild/SRPMS/*.src.rpm

retrieve-srpm:
	cp rpmbuild/SRPMS/* $(outdir)

retrieve-rpm:
	cp rpmbuild/RPMS/*/* $(outdir)

clean:
	rm -rf rpmbuild
	rm -f $(notdir $(SOURCE))
	rm -f *.rpm
