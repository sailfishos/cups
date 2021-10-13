%global use_alternatives 0
%global lspp 0

# {_exec_prefix}/lib/cups is correct, even on x86_64.
# It is not used for shared objects but for executables.
# It's more of a libexec-style ({_libexecdir}) usage,
# but we use lib for compatibility with 3rd party drivers (at upstream request).
%global cups_serverbin %{_exec_prefix}/lib/cups

Summary: Common Unix Printing System
Name: cups
Version: 2.3.1
Release: 1%{?dist}
License: ASL 2.0 with exceptions for GPL2/LGPL2
Url: http://www.cups.org/
Source: %{name}-%{version}.tar.bz2
# Pixmap for desktop file
Source1: cupsprinter.png
# Logrotate configuration
Source2: cups.logrotate
# Backend for NCP protocol
Source3: ncp.backend
Source4: macros.cups


# PAM enablement, very old patch, not even git can track when or why
# the patch was added.
Patch1: cups-system-auth.patch
# cups-config from devel package conflicted on multilib arches,
# fixed hack with pkg-config calling for gnutls' libdir variable
Patch2: cups-multilib.patch
# if someone makes a change to banner files, then there will <banner>.rpmnew
# with next update of cups-filters - this patch makes sure the banner file 
# changed by user is used and .rpmnew or .rpmsave is ignored
# Note: This could be rewrite with use a kind of #define and send to upstream
Patch3: cups-banners.patch
# don't export ssl libs to cups-config - can't find the reason.
Patch4: cups-no-export-ssllibs.patch
# enables old uri usb:/dev/usb/lp0 - leave it here for users of old printers
Patch5: cups-direct-usb.patch
# fix for redhat dbus spooler - adding new dbus functions to backend/ipp.c
# -> initialize dbus connection and sending dbus broadcast about job queued
# on remote queue with QueueChanged type for PRINTER_CHANGED, JOB_STATE_CHANGED
# and PRINTER_STATE_CHANGED events 
Patch6: cups-eggcups.patch
# when system workload is high, timeout for cups-driverd can be reached -
# increase the timeout
Patch7: cups-driverd-timeout.patch
# cupsd implement its own logrotate, but when MaxLogSize 0 is used, logrotated
# takes care of it
Patch8: cups-logrotate.patch
# usb backend didn't get any notification about out-of-paper because of kernel 
Patch9: cups-usb-paperout.patch
# uri compatibility with old Fedoras
Patch10: cups-uri-compat.patch
# fixing snmp oid for hp printer - upstream doesn't want to support too much
# snmp backend, because it's deprecated
Patch11: cups-hp-deviceid-oid.patch
# same as HP OID
Patch12: cups-ricoh-deviceid-oid.patch
# change to notify type, because when it fails to start, it gives a error
# message + renaming org.cups.cupsd names, because we have cups units in
# in older Fedoras
Patch13: cups-systemd-socket.patch
# use IP_FREEBIND, because cupsd cannot bind to not yet existing IP address
# by default
Patch14: cups-freebind.patch
# add support of multifile
Patch15: cups-ipp-multifile.patch
# prolongs web ui timeout
Patch16: cups-web-devices-timeout.patch
# needs to be set to Yes to avoid race conditions
Patch17: cups-synconclose.patch
# failover backend for implementing failover functionality
# TODO: move it to the cups-filters upstream
Patch19: cups-failover-backend.patch

# reported upstream
# adds logs when job fails due bad conversion
Patch20: cups-filter-debug.patch
# add device id for dymo printer
Patch21: cups-dymo-deviceid.patch

Patch22: cups-Revert-Use-iterator-for-CRL-Issue-5532.patch

# selinux and audit enablement for CUPS - needs work and CUPS upstream wants
# to have these features implemented their way in the future
Patch100: cups-lspp.patch


BuildRequires: pam-devel
BuildRequires: pkgconfig(gnutls)
BuildRequires: libacl-devel
BuildRequires: pkgconfig(libusb-1.0)
BuildRequires: pkgconfig(libsystemd)
BuildRequires: pkgconfig(dbus-1)



BuildRequires: automake
# needed for decompressing functions when reading from gzipped ppds
BuildRequires: zlib-devel

# -fstack-protector-all requires GCC 4.0.1
BuildRequires: gcc >= 4.0.1

%if %{lspp}
BuildRequires: libselinux-devel >= 1.23
BuildRequires: audit-libs-devel >= 1.1
%endif

Requires: dbus

# Requires working PrivateTmp (bug #807672)
Requires(pre): systemd
Requires(post): systemd
Requires(post): grep, sed
Requires(preun): systemd
Requires(postun): systemd

# We ship udev rules which use setfacl.
Requires: systemd
Requires: acl

Requires: %{name}-libs%{?_isa} = %{version}-%{release}
%if %{use_alternatives}
Provides: /usr/bin/lpq /usr/bin/lpr /usr/bin/lp /usr/bin/cancel /usr/bin/lprm /usr/bin/lpstat
Requires: /usr/sbin/alternatives
%endif

%package devel
Summary: Common Unix Printing System - development environment
License: LGPLv2
Requires: %{name}-libs%{?_isa} = %{version}-%{release}
Requires: gnutls-devel
Requires: zlib-devel
Provides: cupsddk-devel

%package libs
Summary: Common Unix Printing System - libraries
License: LGPLv2 and zlib

%package lpd
Summary: Common Unix Printing System - lpd emulation
Requires: %{name} = %{version}-%{release}
Requires: %{name}-libs%{?_isa} = %{version}-%{release}

%package ipptool
Summary: Common Unix Printing System - tool for performing IPP requests
Requires: %{name}-libs%{?_isa} = %{version}-%{release}

%package printerapp
Summary: CUPS printing system - tools for printer application
Requires: %{name}-libs%{?_isa} = %{version}-%{release}

%description
The Common UNIX Printing System provides a portable printing layer for 
UNIX® operating systems. It has been developed by Apple Inc.
to promote a standard printing solution for all UNIX vendors and users.
CUPS provides the System V and Berkeley command-line interfaces.

%description devel
The Common UNIX Printing System provides a portable printing layer for
UNIX® operating systems. This is the development package for creating
additional printer drivers, and other CUPS services.

%description libs
The Common UNIX Printing System provides a portable printing layer for
UNIX® operating systems. It has been developed by Apple Inc.
to promote a standard printing solution for all UNIX vendors and users.
CUPS provides the System V and Berkeley command-line interfaces.
The cups-libs package provides libraries used by applications to use CUPS
natively, without needing the lp/lpr commands.

%description lpd
The Common UNIX Printing System provides a portable printing layer for 
UNIX® operating systems. This is the package that provides standard 
lpd emulation.

%description ipptool
Sends IPP requests to the specified URI and tests and/or displays the results.

%description printerapp
Provides IPP everywhere printer application ippeveprinter and tools for printing
PostScript and HP PCL document formats - ippevepcl and ippeveps. The printer
application enables older printers for IPP everywhere standard - so if older printer
is installed with a printer application, its print queue acts as IPP everywhere printer
to CUPS daemon. This solution will substitute printer drivers and raw queues in the future.

%prep
%setup -q -n %{name}-%{version}/%{name}
# Use the system pam configuration.
%patch1 -p1 -b .system-auth
# Prevent multilib conflict in cups-config script.
%patch2 -p1 -b .multilib
# Ignore rpm save/new files in the banners directory.
%patch3 -p1 -b .banners
# Don't export SSLLIBS to cups-config.
%patch4 -p1 -b .no-export-ssllibs
# Allow file-based usb device URIs.
%patch5 -p1 -b .direct-usb
# Increase driverd timeout to 70s to accommodate foomatic (bug #744715).
%patch7 -p1 -b .driverd-timeout
# Re-open the log if it has been logrotated under us.
%patch8 -p1 -b .logrotate
# Support for errno==ENOSPACE-based USB paper-out reporting.
%patch9 -p1 -b .usb-paperout
# Allow the usb backend to understand old-style URI formats.
%patch10 -p1 -b .uri-compat
# Add an SNMP query for HP's device ID OID (STR #3552).
%patch11 -p1 -b .hp-deviceid-oid
# Add an SNMP query for Ricoh's device ID OID (STR #3552).
%patch12 -p1 -b .ricoh-deviceid-oid
# Make cups.service Type=notify (bug #1088918).
%patch13 -p1 -b .systemd-socket
# Use IP_FREEBIND socket option when binding listening sockets (bug #970809).
%patch14 -p1 -b .freebind
# Fixes for jobs with multiple files and multiple formats.
%patch15 -p1 -b .ipp-multifile
# Increase web interface get-devices timeout to 10s (bug #996664).
%patch16 -p1 -b .web-devices-timeout
# Set the default for SyncOnClose to Yes.
%patch17 -p1 -b .synconclose
# Add failover backend (bug #1689209)
%patch19 -p1 -b .failover

%if %{lspp}
# LSPP support.
%patch100 -p1 -b .lspp
%endif

# Log extra debugging information if no filters are available.
%patch20 -p1 -b .filter-debug
# Added IEEE 1284 Device ID for a Dymo device (bug #747866).
%patch21 -p1 -b .dymo-deviceid
# Revert Use iterator for CRL Issue 5532
%patch22 -p1 -b .Revert-Use-iterator-for-CRL-Issue-5532.patch

#### UPSTREAMED PATCHES ####

# removed dbus patch - seems breaking things
# Fix implementation of com.redhat.PrinterSpooler D-Bus object.
#%%patch6 -p1 -b .eggcups

# if cupsd is set to log into /var/log/cups, then 'MaxLogSize 0' needs to be
# in cupsd.conf to disable cupsd logrotate functionality and use logrotated
sed -i -e '1iMaxLogSize 0' conf/cupsd.conf.in

# Let's look at the compilation command lines.
perl -pi -e "s,^.SILENT:,," Makedefs.in

f=CREDITS.md
mv "$f" "$f"~
iconv -f MACINTOSH -t UTF-8 "$f"~ > "$f"
rm -f "$f"~

aclocal -I config-scripts
autoconf -f -I config-scripts

%build
export CFLAGS="$RPM_OPT_FLAGS -fstack-protector-all -DLDAP_DEPRECATED=1"
# --enable-debug to avoid stripping binaries
%configure --with-docdir=%{_datadir}/%{name}/www --enable-debug \
%if %{lspp}
	--enable-lspp \
%endif
	--with-exe-file-perm=0755 \
	--with-cupsd-file-perm=0755 \
	--with-log-file-perm=0600 \
	--enable-relro \
	--with-dbusdir=%{_sysconfdir}/dbus-1 \
	--enable-threads \
	--enable-gnutls \
	--with-rundir=/run/cups \
	localedir=%{_datadir}/locale

# If we got this far, all prerequisite libraries must be here.
make %{?_smp_mflags}

%install
make BUILDROOT=%{buildroot} install

rm -rf	%{buildroot}%{_initddir} \
	%{buildroot}%{_sysconfdir}/init.d \
	%{buildroot}%{_sysconfdir}/rc?.d
mkdir -p %{buildroot}%{_unitdir}

find %{buildroot}%{_datadir}/cups/model -name "*.ppd" |xargs gzip -n9f

%if %{use_alternatives}
pushd %{buildroot}%{_bindir}
for i in cancel lp lpq lpr lprm lpstat; do
	mv $i $i.cups
done
cd %{buildroot}%{_sbindir}
mv lpc lpc.cups
cd %{buildroot}%{_mandir}/man1
for i in cancel lp lpq lpr lprm lpstat; do
	mv $i.1 $i-cups.1
done
cd %{buildroot}%{_mandir}/man8
mv lpc.8 lpc-cups.8
popd
%endif

mv %{buildroot}%{_unitdir}/org.cups.cupsd.path %{buildroot}%{_unitdir}/cups.path
mv %{buildroot}%{_unitdir}/org.cups.cupsd.service %{buildroot}%{_unitdir}/cups.service
mv %{buildroot}%{_unitdir}/org.cups.cupsd.socket %{buildroot}%{_unitdir}/cups.socket
mv %{buildroot}%{_unitdir}/org.cups.cups-lpd.socket %{buildroot}%{_unitdir}/cups-lpd.socket
mv %{buildroot}%{_unitdir}/org.cups.cups-lpd@.service %{buildroot}%{_unitdir}/cups-lpd@.service
/bin/sed -i -e "s,org.cups.cupsd,cups,g" %{buildroot}%{_unitdir}/cups.service

mkdir -p %{buildroot}%{_datadir}/pixmaps %{buildroot}%{_sysconfdir}/X11/sysconfig %{buildroot}%{_sysconfdir}/X11/applnk/System %{buildroot}%{_sysconfdir}/logrotate.d
install -c -m 644 %{SOURCE1} %{buildroot}%{_datadir}/pixmaps
install -c -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/cups
install -c -m 755 %{SOURCE3} %{buildroot}%{cups_serverbin}/backend/ncp

# Ship an rpm macro for where to put driver executables.
mkdir -p %{buildroot}%{_sysconfdir}/rpm/
install -m 0644 %{SOURCE4} %{buildroot}%{_sysconfdir}/rpm/

# Ship a printers.conf file, and a client.conf file.  That way, they get
# their SELinux file contexts set correctly.
touch %{buildroot}%{_sysconfdir}/cups/printers.conf
touch %{buildroot}%{_sysconfdir}/cups/classes.conf
touch %{buildroot}%{_sysconfdir}/cups/client.conf
touch %{buildroot}%{_sysconfdir}/cups/subscriptions.conf
touch %{buildroot}%{_sysconfdir}/cups/lpoptions

# LSB 3.2 printer driver directory
mkdir -p %{buildroot}%{_datadir}/ppd

# Remove unshipped files.
rm -rf %{buildroot}%{_mandir}/cat? %{buildroot}%{_mandir}/*/cat?
rm -f %{buildroot}%{_datadir}/applications/cups.desktop
rm -rf %{buildroot}%{_datadir}/icons
# there are pdf-banners shipped with cups-filters (#919489)
rm -rf %{buildroot}%{_datadir}/cups/banners
rm -f %{buildroot}%{_datadir}/cups/data/testprint

# install /usr/lib/tmpfiles.d/cups.conf (bug #656566, bug #893834)
mkdir -p ${RPM_BUILD_ROOT}%{_tmpfilesdir}
cat > ${RPM_BUILD_ROOT}%{_tmpfilesdir}/cups.conf <<EOF
# See tmpfiles.d(5) for details

d /run/cups 0755 root lp -
d /run/cups/certs 0511 lp sys -

d /var/spool/cups/tmp - - - 30d
EOF

# /usr/lib/tmpfiles.d/cups-lp.conf (bug #812641)
cat > ${RPM_BUILD_ROOT}%{_tmpfilesdir}/cups-lp.conf <<EOF
# Legacy parallel port character device nodes, to trigger the
# auto-loading of the kernel module on access.
#
# See tmpfiles.d(5) for details

c /dev/lp0 0660 root lp - 6:0
c /dev/lp1 0660 root lp - 6:1
c /dev/lp2 0660 root lp - 6:2
c /dev/lp3 0660 root lp - 6:3
EOF

find %{buildroot} -type f -o -type l | sed '
s:.*\('%{_datadir}'/\)\([^/_]\+\)\(.*\.po$\):%lang(\2) \1\2\3:
/^%lang(C)/d
/^\([^%].*\)/d
' > %{name}.lang

%post
%systemd_post %{name}.path %{name}.socket %{name}.service

# Remove old-style certs directory; new-style is /var/run
# (see bug #194581 for why this is necessary).
rm -rf %{_sysconfdir}/cups/certs
rm -f %{_localstatedir}/cache/cups/*.ipp %{_localstatedir}/cache/cups/*.cache
%if %{use_alternatives}
/usr/sbin/alternatives --install %{_bindir}/lpr print %{_bindir}/lpr.cups 40 \
	 --slave %{_bindir}/lp print-lp %{_bindir}/lp.cups \
	 --slave %{_bindir}/lpq print-lpq %{_bindir}/lpq.cups \
	 --slave %{_bindir}/lprm print-lprm %{_bindir}/lprm.cups \
	 --slave %{_bindir}/lpstat print-lpstat %{_bindir}/lpstat.cups \
	 --slave %{_bindir}/cancel print-cancel %{_bindir}/cancel.cups \
	 --slave %{_sbindir}/lpc print-lpc %{_sbindir}/lpc.cups \
	 --slave %{_mandir}/man1/cancel.1.gz print-cancelman %{_mandir}/man1/cancel-cups.1.gz \
	 --slave %{_mandir}/man1/lp.1.gz print-lpman %{_mandir}/man1/lp-cups.1.gz \
	 --slave %{_mandir}/man8/lpc.8.gz print-lpcman %{_mandir}/man8/lpc-cups.8.gz \
	 --slave %{_mandir}/man1/lpq.1.gz print-lpqman %{_mandir}/man1/lpq-cups.1.gz \
	 --slave %{_mandir}/man1/lpr.1.gz print-lprman %{_mandir}/man1/lpr-cups.1.gz \
	 --slave %{_mandir}/man1/lprm.1.gz print-lprmman %{_mandir}/man1/lprm-cups.1.gz \
	 --slave %{_mandir}/man1/lpstat.1.gz print-lpstatman %{_mandir}/man1/lpstat-cups.1.gz
%endif
exit 0

%post lpd
%systemd_post cups-lpd.socket
exit 0

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%preun
%systemd_preun %{name}.path %{name}.socket %{name}.service

%if %{use_alternatives}
if [ $1 -eq 0 ] ; then
	/usr/sbin/alternatives --remove print %{_bindir}/lpr.cups
fi
%endif
exit 0

%preun lpd
%systemd_preun cups-lpd.socket
exit 0

%postun
%systemd_postun_with_restart %{name}.path %{name}.socket %{name}.service
exit 0

%postun lpd
%systemd_postun_with_restart cups-lpd.socket
exit 0

%triggerin -- samba-client
ln -sf ../../../bin/smbspool %{cups_serverbin}/backend/smb || :
exit 0

%triggerun -- samba-client
[ $2 = 0 ] || exit 0
rm -f %{cups_serverbin}/backend/smb

%triggerin -- samba4-client
ln -sf %{_bindir}/smbspool %{cups_serverbin}/backend/smb || :
exit 0

%triggerun -- samba4-client
[ $2 = 0 ] || exit 0
rm -f %{cups_serverbin}/backend/smb

%files -f %{name}.lang
%doc README.md CREDITS.md CHANGES.md
%dir %attr(0755,root,lp) %{_sysconfdir}/cups
%dir %attr(0755,root,lp) /run/cups
%dir %attr(0511,lp,sys) /run/cups/certs
%{_prefix}/lib/tmpfiles.d/cups.conf
%{_prefix}/lib/tmpfiles.d/cups-lp.conf
%verify(not md5 size mtime) %config(noreplace) %attr(0640,root,lp) %{_sysconfdir}/cups/cupsd.conf
%attr(0640,root,lp) %{_sysconfdir}/cups/cupsd.conf.default
%verify(not md5 size mtime) %config(noreplace) %attr(0640,root,lp) %{_sysconfdir}/cups/cups-files.conf
%attr(0640,root,lp) %{_sysconfdir}/cups/cups-files.conf.default
%verify(not md5 size mtime) %config(noreplace) %attr(0644,root,lp) %{_sysconfdir}/cups/client.conf
%verify(not md5 size mtime) %config(noreplace) %attr(0600,root,lp) %{_sysconfdir}/cups/classes.conf
%verify(not md5 size mtime) %config(noreplace) %attr(0600,root,lp) %{_sysconfdir}/cups/printers.conf
%verify(not md5 size mtime) %config(noreplace) %attr(0644,root,lp) %{_sysconfdir}/cups/snmp.conf
%attr(0640,root,lp) %{_sysconfdir}/cups/snmp.conf.default
%verify(not md5 size mtime) %config(noreplace) %attr(0640,root,lp) %{_sysconfdir}/cups/subscriptions.conf
%verify(not md5 size mtime) %config(noreplace) %attr(0644,root,lp) %{_sysconfdir}/cups/lpoptions
%dir %attr(0755,root,lp) %{_sysconfdir}/cups/ppd
%dir %attr(0700,root,lp) %{_sysconfdir}/cups/ssl
%config(noreplace) %{_sysconfdir}/pam.d/cups
%config(noreplace) %{_sysconfdir}/logrotate.d/cups
%dir %{_datadir}/%{name}/www
%dir %{_datadir}/%{name}/www/de
%dir %{_datadir}/%{name}/www/es
%dir %{_datadir}/%{name}/www/ja
%dir %{_datadir}/%{name}/www/ru
%{_datadir}/%{name}/www/images
%{_datadir}/%{name}/www/*.css
%{_datadir}/%{name}/www/index.html
%{_datadir}/%{name}/www/help
%{_datadir}/%{name}/www/robots.txt
%{_datadir}/%{name}/www/de/index.html
%{_datadir}/%{name}/www/es/index.html
%{_datadir}/%{name}/www/ja/index.html
%{_datadir}/%{name}/www/ru/index.html
%{_datadir}/%{name}/www/pt_BR/index.html
%{_datadir}/%{name}/www/apple-touch-icon.png
%dir %{_datadir}/%{name}/usb
%{_datadir}/%{name}/usb/org.cups.usb-quirks
%{_unitdir}/%{name}.service
%{_unitdir}/%{name}.socket
%{_unitdir}/%{name}.path
%{_bindir}/cupstestppd
%{_bindir}/cancel*
%{_bindir}/lp*
%{_bindir}/ppd*
%dir %{cups_serverbin}
%{cups_serverbin}/backend
%{cups_serverbin}/cgi-bin
%dir %{cups_serverbin}/daemon
%{cups_serverbin}/daemon/cups-deviced
%{cups_serverbin}/daemon/cups-driverd
%{cups_serverbin}/daemon/cups-exec
%{cups_serverbin}/notifier
%{cups_serverbin}/filter
%{cups_serverbin}/monitor
%{cups_serverbin}/driver
%{_mandir}/man[1578]/*
# devel subpackage
%exclude %{_mandir}/man1/cups-config.1.gz
# ipptool subpackage
%exclude %{_mandir}/man1/ipptool.1.gz
%exclude %{_mandir}/man5/ipptoolfile.5.gz
# lpd subpackage
%exclude %{_mandir}/man8/cups-lpd.8.gz
%{_sbindir}/*
%dir %{_datadir}/cups/templates
%dir %{_datadir}/cups/templates/de
%dir %{_datadir}/cups/templates/es
%dir %{_datadir}/cups/templates/ja
%dir %{_datadir}/cups/templates/ru
%dir %{_datadir}/cups/templates/pt_BR
%{_datadir}/cups/templates/*.tmpl
%{_datadir}/cups/templates/de/*.tmpl
%{_datadir}/cups/templates/fr/*.tmpl
%{_datadir}/cups/templates/es/*.tmpl
%{_datadir}/cups/templates/ja/*.tmpl
%{_datadir}/cups/templates/ru/*.tmpl
%{_datadir}/cups/templates/pt_BR/*.tmpl
%dir %attr(1770,root,lp) %{_localstatedir}/spool/cups/tmp
%dir %attr(0710,root,lp) %{_localstatedir}/spool/cups
%dir %attr(0755,lp,sys) %{_localstatedir}/log/cups
%{_datadir}/pixmaps/cupsprinter.png
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/cups.conf
%dir %{_datadir}/cups
%dir %{_datadir}/cups/data
%dir %{_datadir}/cups/drv
%{_datadir}/cups/drv/sample.drv
%{_datadir}/cups/examples
%dir %{_datadir}/cups/mime
%{_datadir}/cups/mime/mime.types
%{_datadir}/cups/mime/mime.convs
%dir %{_datadir}/cups/model
%dir %{_datadir}/cups/ppdc
%{_datadir}/cups/ppdc/*.defs
%{_datadir}/cups/ppdc/*.h
%dir %{_datadir}/ppd

%files libs
%license LICENSE
%license NOTICE
%{_libdir}/*.so.*

%files devel
%{_bindir}/cups-config
%{_libdir}/*.so
%{_includedir}/cups
%{_mandir}/man1/cups-config.1*
%{_sysconfdir}/rpm/macros.cups

%files lpd
%{_unitdir}/cups-lpd.socket
%{_unitdir}/cups-lpd@.service
%{cups_serverbin}/daemon/cups-lpd
%{_mandir}/man8/cups-lpd.8.gz

%files ipptool
%{_bindir}/ipptool
%dir %{_datadir}/cups/ipptool
%{_datadir}/cups/ipptool/*
%{_mandir}/man1/ipptool.1.gz
%{_mandir}/man5/ipptoolfile.5.gz

%files printerapp
%{_bindir}/ippeveprinter
%dir %{cups_serverbin}/command
%{cups_serverbin}/command/ippevepcl
%{cups_serverbin}/command/ippeveps
%{_mandir}/man1/ippeveprinter.1.gz
%{_mandir}/man7/ippevepcl.7.gz
