%global giturl  https://gitlab.com/tuxedocomputers/development/packages/tuxedo-drivers/
%define buildforkernels akmod
%global AkmodsBuildRequires shyaml
%global debug_package %{nil}

Name:           tuxedo-drivers-kmod

Version:        4.22.2
Release:        %autorelease
Summary:        Drivers for Tuxedo computers

Group:          System Environment/Kernel

License:        GPLv2
URL:            https://github.com/darrencocco/tuxedo-drivers-kmod
Source0:        %{giturl}/-/archive/v%{version}/tuxedo-drivers-v%{version}.tar.gz
Source1:        extract_modules.sh
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Recommends:     udev-hid-bpf

BuildRequires:  kmodtool
BuildRequires:  make
BuildRequires:  gcc
BuildRequires:  shyaml

%description
Collection of Linux drivers for Tuxedo computers.

%{expand:%(kmodtool --target %{_target_cpu} --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }

# Define the userspace tools package
%package -n tuxedo-drivers
Summary: Common files for Tuxedo drivers.
Provides: tuxedo-drivers-kmod-common = %{version}
Requires: tuxedo-drivers-kmod >= %{version}

%description -n tuxedo-drivers
Configuration for Tuxedo computer drivers.

%prep
%autosetup -n tuxedo-drivers-v%{version} -p 1
cp %{SOURCE1} .

# error out if there was something wrong with kmodtool
%{?kmodtool_check}

# print kmodtool output for debugging purposes:
kmodtool --target %{_target_cpu} --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null

for kernel_version  in %{?kernel_versions} ; do
  mkdir -p _kmod_build_${kernel_version%%___*}
  cp -ar src/* _kmod_build_${kernel_version%%___*}/
done

%build

for kernel_version  in %{?kernel_versions} ; do
  make V=1 %{?_smp_mflags} -C ${kernel_version##*___} M=${PWD}/_kmod_build_${kernel_version%%___*} VERSION=v%{version} modules
done

%install
# Install kernel modules
eval $(./extract_modules.sh base_package.yml)
for kernel_version in %{?kernel_versions}; do
 mkdir -p %{buildroot}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/
 for module_path in "${ARRAY[@]}"; do
   module_name=$(basename ${module_path})
   install -D -m 755 _kmod_build_${kernel_version%%___*}/${module_path}.ko %{buildroot}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/
   chmod a+x %{buildroot}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/${module_name}.ko
 done
done
%{?akmod_install}

# Install userspace config
mkdir -p %{buildroot}%{_usr}/lib
mv files/usr/lib/modprobe.d %{buildroot}%{_usr}/lib
mv files/usr/lib/udev %{buildroot}%{_usr}/lib

%files -n tuxedo-drivers
%{_usr}/lib/modprobe.d/*
%{_usr}/lib/udev/*
%doc README.md
%license LICENSE

%changelog
* Wed Apr 29 2026 Maximilian Arnold - 4.22.2-1
- Fix debian postinst dkms errors in chroot

* Fri Apr 10 2026 Werner Sembach - 4.22.1-1
- Fix alpm dkms package folder name

* Thu Apr 09 2026 Werner Sembach - 4.22.0-1
- Add support for InfinityBook Max 16 Gen10 AMD
- Fix pulsating fan on several devices
- Fix CI tests
- Fix Makefile package target

* Mon Mar 23 2026 Werner Sembach - 4.21.3-1
- Fix upgrade bug

* Fri Mar 13 2026 Werner Sembach - 4.21.2-1
- Fix charging profile not persisting across power events

* Thu Mar 05 2026 Werner Sembach - 4.21.1-1
- Fix license information

* Tue Feb 24 2026 Werner Sembach - 4.21.0-1
- Use Simple Package Creator
- Fix pulsating fans for InfinityBook Pro 15 Gen10
- Fix keyboard color scaling on InfinityBook Max 15 Gen10
- Enable hidden overclocking bios menu

* Thu Jan 22 2026 Werner Sembach - 4.20.1-1
- Update docker url in CI

* Tue Jan 20 2026 Werner Sembach - 4.19.0-1
- Add InfinityBook Max 16 Gen10 Intel support

* Tue Dec 16 2025 Werner Sembach - 4.18.2-1
- Change default of EC write method for NB02 to potentially fix stuck fanspeed

* Wed Nov 26 2025 Werner Sembach - 4.18.1-1
- Fix keyboard backlight support for IBP Gen10 Intel
- Remove Fedora 40 from build tests
- Add Fedora 43 to build tests
- Fix 4.18.0 changelog

* Mon Nov 03 2025 Werner Sembach - 4.18.0-1
- Add InfinityBook Pro Gen10 Intel support
- Add InfinityBook Max Gen10 AMD support

* Thu Oct 16 2025 Werner Sembach - 4.17.0-1
- Add display local dimming toggle for Stellaris Gen 7
- Inverted charging prio supported/unsupported list
- Run build test also after merge in main

* Wed Oct 01 2025 Werner Sembach - 4.16.0-1
- Fix min TDP for Stellaris Gen7 AMD
- Add fix for Huawei LTE modules
- Remove amdgpu-firmware package from recommended
- Add debian 13 and fedora 42 to build tests
- Remove undocumented config file
- Fix backlight control on some NB02 devices
- Blacklist Uniwill upstream driver

* Fri Aug 29 2025 Werner Sembach - 4.15.4-1
- Fix fan control unresponsive on older NB02 devices

* Mon Aug 25 2025 Werner Sembach - 4.15.3-1
- Fix pulsating fan on NB02 devices by making TD full fan mode aware
- Readd and fix `make all` and `make install` targets as they are required for
- Add .editorconfig for developer convenience

* Mon Aug 18 2025 Tim Guttzeit - 4.15.2-1
- change tuxedo-linux-firmware-amdgpu to Recommends

* Thu Aug 14 2025 Maximilian Arnold - 4.15.1-1
- add tuxedo-linux-firmware-amdgpu as Depends

* Wed Aug 06 2025 Tim Guttzeit - 4.15.0-1
- Stellaris Gen7 AMD: Fix keyboard color, TGP, TDP;
- Stellaris Gen7 AMD: Remove unsupported USB-C Charging Prios
- Stellaris Gen7 AMD: Add AC Autoboot and USB Powershare features
- IBP Gen10: Fix ID changes
- IBP Gen10: Add IDs to power profiles and five step keyboard backlight

* Wed Jul 30 2025 Tim Guttzeit - 4.14.4-1
- Move udev rules from tuxedo-fix-config-files into tuxedo-drivers

* Tue Jul 15 2025 Werner Sembach - 4.14.3-1
- Fix Stellaris Gen7 leaving custom profile upon power event

* Tue Jul 01 2025 Werner Sembach - 4.14.2-1
- More small fixes for Stellaris Gen7 support
- Small fix for IBP Gen10 support

* Tue Jun 17 2025 Werner Sembach - 4.14.1-1
- Cleanup Makefile
- Update Readme
- Fix NB02 devices have bogus mouse device
- Harmonize config file names

* Wed Jun 11 2025 Werner Sembach - 4.14.0-1
- Several small fixes for Stellaris Gen7 support
- Add wake on power setting for supported devices
- Add power share setting for supported devices

* Thu May 15 2025 Werner Sembach - 4.13.1-1
- InfinityFlex: Make FN-key no longer disable touchpad
- NB02: Make FN-key no longer spam dmesg

* Wed May 07 2025 Werner Sembach - 4.13.0-1
- Fix touchpad toggle key on NB02 on wayland
- Fix Aura 14/15 Gen4 Webcam switch not disapearing when deactivated in BIOS
- Add udev-hid-bpf recommendation for Sirius 16 Gen1/2 keyboard fix
- Fix build errors with Kernel 6.14 and 6.15

* Tue Feb 18 2025 Werner Sembach - 4.12.2-1
- Fix IBP Gen9 keyboard backlight not controllable after cold boot until first
- This will be the last version officially supported on Ubuntu 22.04.

* Mon Jan 27 2025 Werner Sembach - 4.12.1-1
- Change device check for fixed 5 color kbl on NB02 devices from EC-ID to DMI
- Cleanup changelog and order chronologically
- Generate rpm changelog from deb changelog

* Wed Jan 15 2025 Werner Sembach - 4.12.0-1
- Add keyboard backlight support for IBP Gen9
- Add automatic compile tests
- Fix low fan speed rounding issue between off and 25%

* Wed Dec 11 2024 Werner Sembach - 4.11.7-1
- Avoid floating point to be more widely compatible

* Thu Dec 05 2024 Werner Sembach - 4.11.6-1
- Fix build against kernel 5.15

* Thu Dec 05 2024 Werner Sembach - 4.11.5-1
- Block 1%-24% fanspeeds and round to 0% or 25% respectifly to avoid irregular

* Tue Nov 26 2024 Werner Sembach - 4.11.4-1
- Remove buggy autoreload on install
- Fix CPU power handling on Stellaris 16 Gen6
- Fix instant wakeup on Stellaris Slim 15 Gen6 AMD

* Mon Nov 18 2024 Werner Sembach - 4.11.3-1
- Fix crashes on package install

* Wed Nov 13 2024 Werner Sembach - 4.11.2-1
- Fix missing module reload handling in install scripts

* Wed Nov 13 2024 Werner Sembach - 4.11.1-1
- Fix build with different kernels

* Tue Nov 12 2024 Werner Sembach - 4.11.0-1
- Add TUXI (TUXEDO Interface) acpi driver
- Fix InfinityBook Pro v3 keyboard backlight levels

* Wed Nov 06 2024 Werner Sembach - 4.10.2-1
- Fix color scaling for Stellaris 16 Gen6 Intel

* Tue Nov 05 2024 Werner Sembach - 4.10.1-1
- Fix compile errors with linux 6.12
- Fix compile warnings

* Thu Oct 24 2024 Werner Sembach - 4.10.0-1
- Fix IBP Gen9 fan control hickups
- Add basic lightbar support for new devices

* Tue Oct 15 2024 Werner Sembach - 4.9.0-1
- Add power profiles support for IBP Gen9
- Add Stellaris Slim Gen6 TDP support
- Fix TDP set for Stellaris Gen6 devices

* Mon Sep 30 2024 Werner Sembach - 4.8.0-1
- Add support for InfinityFlex toggle touchscreen button
- Update ReadMe

* Mon Sep 16 2024 Werner Sembach - 4.7.0-1
- Add Support for the TUXEDO InfinityFlex Gen1

* Mon Sep 02 2024 Werner Sembach - 4.6.3-1
- Fix compile for kernel 6.11

* Tue Aug 13 2024 Werner Sembach - 4.6.2-1
- Fix compile for kernel 6.10

* Wed Jul 24 2024 Werner Sembach - 4.6.1-1
- Fix compiler warnings with `Wstrict-prototypes`
- Fix compile error on openSUSE

* Thu Jul 11 2024 Werner Sembach - 4.6.0-1
- Enable fn_lock on Aura Gen3 refresh

* Wed Jul 10 2024 Werner Sembach - 4.5.4-1
- Fix keyboard backlight quirk list error for Stellaris Gen5 and Gen6

* Thu Jun 27 2024 Werner Sembach - 4.5.3-1
- Fix touchpad toggle key sometimes not working
- Fix fans having realy slow ramp up speed
- Fix fans sometimes shutting off under sustained load

* Wed Jun 19 2024 Christoffer Sandberg - 4.5.2-1
- Rename Stellaris Slim Gen1 => Gen6 for the release

* Fri Jun 07 2024 Werner Sembach - 4.5.1-1
- Improve Pulse Gen3 and Gen4 fan control for newer firmware
- Add keyboard backlight color sclaing for Stellaris Lite Gen1

* Sat May 25 2024 Werner Sembach - 4.5.0-1
- Fix dynamic boost being stuck at 5W
- Add Pulse Gen4 support
- Add Sirius Gen2 support
- Add Pulse Gen3 and Gen4 fan control support

* Wed May 08 2024 Werner Sembach - 4.4.3-1
- Stop generating transitional packages

* Fri Apr 26 2024 Werner Sembach - 4.4.2-1
- Fix Dynamic Boost default
- Dev/Debug: Pass through make arguments to sub makes

* Wed Apr 17 2024 Werner Sembach - 4.4.1-1
- Fix tint in keyboard backlight for Stellaris 17 Gen6

* Mon Apr 08 2024 Werner Sembach - 4.4.0-1
- Split IBPG7 TDP definitions for mk1/mk2 and update values
- Initial Stellaris Gen6 support

* Thu Mar 07 2024 Werner Sembach - 4.3.2-1
- Restart UPower upon instal and remove because it does not handle
- Add troubleshooting section to ReadMe
- Touchups on package and make scripts

* Tue Mar 05 2024 Werner Sembach - 4.3.1-1
- Clarify transitional packages and obsoletes
- Add systemd boot delay fix

* Thu Feb 29 2024 Werner Sembach - 4.3.0-1
- Implement nb05 (Pulse Gen3) gauge key (opens TCC)

* Mon Feb 19 2024 Werner Sembach - 4.2.2-1
- Fix compiler error for older kernels by naming unused variables

* Wed Feb 07 2024 Werner Sembach - 4.2.1-1
- Fix compile issue on Linux 5.15

* Tue Feb 06 2024 Werner Sembach - 4.2.0-1
- Add basic nb05 keyboard backlight driver
- Remove unsupported IBS Gen6 from flexicharger settings
- Clean build and runtime error/warning log
- Update README
- Add capability to control NVIDIA cTGP on nb02 devices

* Thu Jan 25 2024 Werner Sembach - 4.1.2-1
- Fix high cpu load caused by profile write logic bug

* Tue Jan 23 2024 Werner Sembach - 4.1.1-1
- Fix keyboard backlight detection for Stellaris Gen5 AMD

* Wed Jan 17 2024 Werner Sembach - 4.1.0-1
- Add nb04 driver collection (so far used by Sirius 16 Gen1)

* Thu Dec 28 2023 Werner Sembach - 4.0.3-1
- Fix modprobe conf file not applying

* Thu Dec 21 2023 Werner Sembach - 4.0.2-1
- nb01: Charging thresholds fixes

* Fri Dec 15 2023 Werner Sembach - 4.0.1-1
- Fix build on Ubuntu 22.04 5.15 kernel

* Tue Mar 17 2020 Christoffer Sandberg - 4.0.0-1
- Merge tuxedo-keyboard and tuxedo-keyboard-ite
- Rename package to tuxedo-drivers
- Rework packaging process
- Fn-lock sysfs interface for nb02 and nb01 (newer models with CCC from v4.0)
- Flexicharger sysfs interface for nb01 (new plus legacy which works on some
- Various backlight bugfixes and rework
- nb05 driver collection (so far used by Pulse Gen3)
- Add color scaling for Stellaris Gen5 AMD devices
- Tweak IBPG8 TDP limits
- Add missing IBPG8 TDP definitions
- Polaris/Stellaris AMD Gen5 support
- Aura Gen3 support
- Fix build on certain systems
- Adjusted lightbar USB product exclusion (prevents driver binding to unused
- Lightbar color scaling for Stellaris 17 Gen5
- Quirks for setting missing IBP16Gen8 keyboard layouts
- Fix IBP 16 Gen8 mk1 layout set to 14inch variant layout
- Keyboard backlight support for IBS17Gen8 (white-only)
- Fn backlight key support for IBS17Gen8
- Fix for certain white kbd bl identification on boot (XA15)
- General white-only kbd bl rework to use firmware set on Fn+brightness
- Kernel 6.4 build compatibility fix
- Fallback ROM ID set quirk support
- IBP Gen8 keyboard backlight support
- IBP Gen8 TDP support
- Color scaling for certain one-zone RGB keyboards
- Fix for certain white kbd bl devices (like Pulse) not setting brightness
- Four zone backlight support for Stellaris Gen5
- Experimental buffered writes for Stellaris/Fusion per-key variants
- Fix missing state write on resume for some devices which woke up with
- Add TDP device definitions for Stellaris Intel Gen5
- Add device check on newer cpu gens
- Color scaling for Stellaris Intel Gen5
- Lightbar impl. for Stellaris Gen4/5
- Fix
- KBD BL: Interface rewrite, now generally exported through
- KBD BL: New interface impl. for white backlight keyboards (also
- Note: Old interface is hereby deprecated (and removed)
- Leds interface support (/sys/class/leds)
- Fix upcoming 6.2 kernel build issue (from github Buddy-Matt)
- Re-write last set charging priority on barrel plug connect
- UW interface performance tweaks (should help with lagging keyboard issues
- Fix IBP14Gen6 second fan not spinning (alternative fan ctl approach)
- Fix some error-lookalike messages in kernel log (aka prevent uw feature
- Enables dynamic boost (max offset) for certain devices needing sw ctl
- Adds charging profile interface for devices supporting charging profiles
- Adds charging priority interface for devices supporting USB-C PD charging
- Add per-device color scaling to ite_8291 driver
- Add additional scaling setting for Stellaris 17 AMD Gen 4
- Add USB ID for Stellaris 17 Gen 4 keyboard backlight
- Reenable fans-off for some devices that got it turned of as a temporary
- Fix default fan curve not being reenabled when tccd is stopped
- Add power profiles and tdp functionality (uw)
- Introduce alternative fan control (uw)
- Fan control parameters from driver
- Fixes missing/broken fan control on newer devices
- Add Stellaris Intel gen 4 lightbar support
- Default lightbar to off
- Add IBS15v6 & IBS17v6 new module name to perf. prof workaround
- Interface modularization (uw)
- Fix Pulse14/15 gen 1 keyboard backlight ctrl dissapearing
- Add IBS14v6 to perf. prof workaround
- Add new Polaris devices gen 2 & gen 3 keyb bl support
- Add Stellaris (gen3) lightbar support
- Fix kernel 5.13 build issue (from github BlackIkeEagle)
- Add another Fusion lightbar ID (from github ArlindoFNeto)
- Add tuxedo-io perf. prof. set (cl)
- Add NS50MU to perf. profile workaround
- Add EDUBOOK1502 to perf. profile workaround
- Add XP gen 11 & 12 to perf. profile workaround
- Clean-up cl driver state init (should fix some init color issues)
- Fixed various possible race conditions on driver init
- Added IBS14v5 to perf. profile workaround
- Added new Aura board name to perf. profile workaround
- Fixed non-initialized firmware fan curve for silent mode (UW)
- Changed default perf. profile to balanced (UW)
- Added XP14 to perf. profile workaround
- Fix broken brightness key reaction for ite_829x
- Attempt to fix ite_829x instability sometimes locking up kernel on
- Fixed clevo keyboard init order
- Added Aura perf. profile workaround
- Added device 048d:6004 to ite_8291
- Added device support (Trinity)
- Fixed uw fan ramp up issues to some extent (workaround)
- Changed structure of clevo interfaces
- Added separate clevo-wmi module with existing functionality
- Added clevo-acpi module with implementation of the
- Added tuxedo-io module (former tuxedo-cc-wmi) into package
- Added initial support for ITE Device(8291) ->  048d:ce00
- Added device support (XMG Fusion)
- Added uniwill lightbar driver (with led_classdev interface)
- Added uniwill keymapping brightness up/down
- Fixed uniwill touchpad toggle (some platforms)
- Fixed module cleanup crash
- Added initial (very basic) support for 048d:8297 LED controller
- Fixed key mapping toggle <=> switch mode
- Default color to white
- Initial experimental release
- Added uw kbd color backlight support
- Restructure to allow for more devices
- Added device support
- Added rudimentary device detection
- Added rfkill key event
- Fix volume button events, ignore
- General key event mapping support
- Events added for backlight and touchpad
- Fix not restoring state on resume
- Fix module autoload issues
- Add standard config tuxedo_keyboard.conf to package
- First version of the ITE keyboard backlight driver
- Has support for ITE Device(829x) ->  0x048d:0x8910
- New packaging
