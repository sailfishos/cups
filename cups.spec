%global use_alternatives 1
%global lspp 0

# This should be macro in systemd, remove when introduced there.
%define _unitdir /lib/systemd/system

# {_exec_prefix}/lib/cups is correct, even on x86_64.
# It is not used for shared objects but for executables.
# It's more of a libexec-style ({_libexecdir}) usage,
# but we use lib for compatibility with 3rd party drivers (at upstream request).
%global cups_serverbin %{_exec_prefix}/lib/cups

Summary: Common Unix Printing System
Name: cups
Version: 1.5.3
Release: 3%{?dist}
License: GPLv2
Group: System Environment/Daemons
Source: http://ftp.easysw.com/pub/cups/%{version}/cups-%{version}-source.tar.bz2
# Pixmap for desktop file
Source2: cupsprinter.png
# LSPP-required ps->pdf filter
Source4: pstopdf
# xinetd config file for cups-lpd service
Source5: cups-lpd
# Logrotate configuration
Source6: cups.logrotate
# Backend for NCP protocol
Source7: ncp.backend
# Cron-based tmpwatch for /var/spool/cups/tmp
Source8: cups.cron
# Filter and PPD for textonly printing
Source9: textonly.filter
Source10: textonly.ppd
Source11: macros.cups
Patch1: cups-no-gzip-man.patch
Patch2: cups-system-auth.patch
Patch3: cups-multilib.patch
Patch4: cups-serial.patch
Patch5: cups-banners.patch
Patch6: cups-serverbin-compat.patch
Patch7: cups-no-export-ssllibs.patch
Patch8: cups-direct-usb.patch
Patch9: cups-lpr-help.patch
Patch10: cups-peercred.patch
Patch11: cups-pid.patch
Patch12: cups-eggcups.patch
Patch13: cups-getpass.patch
Patch14: cups-driverd-timeout.patch
Patch15: cups-strict-ppd-line-length.patch
Patch16: cups-logrotate.patch
Patch17: cups-usb-paperout.patch
Patch18: cups-build.patch
Patch19: cups-res_init.patch
Patch20: cups-filter-debug.patch
Patch21: cups-uri-compat.patch
Patch22: cups-cups-get-classes.patch
Patch23: cups-str3382.patch
Patch25: cups-0755.patch
Patch26: cups-snmp-quirks.patch
Patch27: cups-hp-deviceid-oid.patch
Patch28: cups-dnssd-deviceid.patch
Patch29: cups-ricoh-deviceid-oid.patch

Patch30: cups-avahi-1-config.patch
Patch31: cups-avahi-2-backend.patch
Patch32: cups-avahi-3-timeouts.patch
Patch33: cups-avahi-4-poll.patch
Patch34: cups-avahi-5-services.patch

Patch35: cups-icc.patch
Patch36: cups-systemd-socket.patch

Patch100: cups-lspp.patch

Url: http://www.cups.org/

Requires: /sbin/chkconfig /sbin/service
Requires: %{name}-libs%{?_isa} = %{version}-%{release}
%if %use_alternatives
Provides: /usr/bin/lpq /usr/bin/lpr /usr/bin/lp /usr/bin/cancel /usr/bin/lprm /usr/bin/lpstat
Requires: /usr/sbin/alternatives
%endif

BuildRequires: pam-devel
BuildRequires: gnutls-devel libacl-devel
BuildRequires: pcre-devel
BuildRequires: libjpeg-devel
BuildRequires: libpng-devel
BuildRequires: libtiff-devel
BuildRequires: libusb1-devel
BuildRequires: poppler-utils
BuildRequires: systemd-devel

%if %lspp
BuildRequires: libselinux-devel >= 1.23
BuildRequires: audit-libs-devel >= 1.1
%endif

# -fstack-protector-all requires GCC 4.0.1
BuildRequires: gcc >= 4.0.1

BuildRequires: automake

BuildRequires: dbus-devel >= 0.90
Requires: dbus >= 0.90

# Requires tmpwatch for the cron.daily script (bug #218901).
Requires: tmpwatch

# Requires /etc/tmpfiles.d (bug #656566)
#Requires: systemd-units >= 13
#Requires(post): systemd-units
#Requires(preun): systemd-units
#Requires(postun): systemd-units
#Requires(post): systemd-sysv
# Requires working PrivateTmp (bug #807672)
Requires(pre): systemd >= 37-14

Requires: poppler-utils

# We ship udev rules which use setfacl.
Requires: systemd
Requires: acl

# Make sure we have some filters for converting to raster format.
Requires: ghostscript-cups

%package devel
Summary: Common Unix Printing System - development environment
Group: Development/Libraries
License: LGPLv2
Requires: %{name}-libs%{?_isa} = %{version}-%{release}
Requires: gnutls-devel
Requires: zlib-devel
Obsoletes: cupsddk-devel < 1.2.3-7
Provides: cupsddk-devel = 1.2.3-7

%package libs
Summary: Common Unix Printing System - libraries
Group: System Environment/Libraries
License: LGPLv2

%package lpd
Summary: Common Unix Printing System - lpd emulation
Group: System Environment/Daemons
Requires: %{name} = %{version}-%{release}
Requires: %{name}-libs%{?_isa} = %{version}-%{release}
Requires: xinetd

%package ipptool
Summary: Common Unix Printing System - tool for performing IPP requests
Group: System Environment/Daemons
Requires: %{name}-libs = %{version}-%{release}

%description
The Common UNIX Printing System provides a portable printing layer for 
UNIX® operating systems. It has been developed by Easy Software Products 
to promote a standard printing solution for all UNIX vendors and users. 
CUPS provides the System V and Berkeley command-line interfaces. 

%description devel
The Common UNIX Printing System provides a portable printing layer for 
UNIX® operating systems. This is the development package for creating
additional printer drivers, and other CUPS services.

%description libs
The Common UNIX Printing System provides a portable printing layer for 
UNIX® operating systems. It has been developed by Easy Software Products 
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

%prep
%setup -q
# Don't gzip man pages in the Makefile, let rpmbuild do it.
%patch1 -p1 -b .no-gzip-man
# Use the system pam configuration.
%patch2 -p1 -b .system-auth
# Prevent multilib conflict in cups-config script.
%patch3 -p1 -b .multilib
# Fix compilation of serial backend.
%patch4 -p1 -b .serial
# Ignore rpm save/new files in the banners directory.
%patch5 -p1 -b .banners
# Use compatibility fallback path for ServerBin.
%patch6 -p1 -b .serverbin-compat
# Don't export SSLLIBS to cups-config.
%patch7 -p1 -b .no-export-ssllibs
# Allow file-based usb device URIs.
%patch8 -p1 -b .direct-usb
# Add --help option to lpr.
%patch9 -p1 -b .lpr-help
# Fix compilation of peer credentials support.
%patch10 -p1 -b .peercred
# Maintain a cupsd.pid file.
%patch11 -p1 -b .pid
# Fix implementation of com.redhat.PrinterSpooler D-Bus object.
%patch12 -p1 -b .eggcups
# More sophisticated implementation of cupsGetPassword than getpass.
%patch13 -p1 -b .getpass
# Increase driverd timeout to 70s to accommodate foomatic (bug #744715).
%patch14 -p1 -b .driverd-timeout
# Only enforce maximum PPD line length when in strict mode.
%patch15 -p1 -b .strict-ppd-line-length
# Re-open the log if it has been logrotated under us.
%patch16 -p1 -b .logrotate
# Support for errno==ENOSPACE-based USB paper-out reporting.
%patch17 -p1 -b .usb-paperout
# Simplify the DNSSD parts so they can build using the compat library.
%patch18 -p1 -b .build
# Re-initialise the resolver on failure in httpAddrGetList().
%patch19 -p1 -b .res_init
# Log extra debugging information if no filters are available.
%patch20 -p1 -b .filter-debug
# Allow the usb backend to understand old-style URI formats.
%patch21 -p1 -b .uri-compat
# Fix support for older CUPS servers in cupsGetDests.
%patch22 -p1 -b .cups-get-classes
# Fix temporary filename creation.
%patch23 -p1 -b .str3382
# Use mode 0755 for binaries and libraries where appropriate.
%patch25 -p1 -b .0755
# Handle SNMP supply level quirks (bug #581825).
%patch26 -p1 -b .snmp-quirks
# Add an SNMP query for HP's device ID OID (STR #3552).
%patch27 -p1 -b .hp-deviceid-oid
# Mark DNS-SD Device IDs that have been guessed at with "FZY:1;".
%patch28 -p1 -b .dnssd-deviceid
# Add an SNMP query for Ricoh's device ID OID (STR #3552).
%patch29 -p1 -b .ricoh-deviceid-oid

# Avahi support:
# - discovery in the dnssd backend
# - service announcement in the scheduler
%patch30 -p1 -b .avahi-1-config
%patch31 -p1 -b .avahi-2-backend
%patch32 -p1 -b .avahi-3-timeouts
%patch33 -p1 -b .avahi-4-poll
%patch34 -p1 -b .avahi-5-services

# ICC colord support.
%patch35 -p1 -b .icc

# Add support for systemd socket activation (patch from Lennart
# Poettering).
%patch36 -p1 -b .systemd-socket

%if %lspp
# LSPP support.
%patch100 -p1 -b .lspp
%endif

sed -i -e '1iMaxLogSize 0' conf/cupsd.conf.in

cp %{SOURCE5} cups-lpd.real
perl -pi -e "s,\@LIBDIR\@,%{_libdir},g" cups-lpd.real

# Let's look at the compilation command lines.
perl -pi -e "s,^.SILENT:,," Makedefs.in

# Fix locale code for Norwegian (bug #520379).
mv locale/cups_no.po locale/cups_nb.po

f=CREDITS.txt
mv "$f" "$f"~
iconv -f MACINTOSH -t UTF-8 "$f"~ > "$f"
rm "$f"~

# Rebuild configure script for --enable-avahi.
aclocal -I config-scripts
autoconf -I config-scripts

%build
export CFLAGS="$RPM_OPT_FLAGS -fstack-protector-all -DLDAP_DEPRECATED=1"
# --enable-debug to avoid stripping binaries
%configure --with-docdir=%{_datadir}/%{name}/www --enable-debug \
%if %lspp
	--enable-lspp \
%endif
	--with-log-file-perm=0600 --enable-relro \
	--with-pdftops=pdftops \
	--with-dbusdir=%{_sysconfdir}/dbus-1 \
	--enable-threads --enable-gnutls \
	localedir=%{_datadir}/locale

# If we got this far, all prerequisite libraries must be here.
make %{?_smp_mflags}

%install
make BUILDROOT=$RPM_BUILD_ROOT install 

# Serial backend needs to run as root (bug #212577).
chmod 700 $RPM_BUILD_ROOT%{cups_serverbin}/backend/serial

rm -rf	$RPM_BUILD_ROOT%{_initddir} \
	$RPM_BUILD_ROOT%{_sysconfdir}/init.d \
	$RPM_BUILD_ROOT%{_sysconfdir}/rc?.d
mkdir -p $RPM_BUILD_ROOT%{_unitdir}

find $RPM_BUILD_ROOT%{_datadir}/cups/model -name "*.ppd" |xargs gzip -n9f

%if %use_alternatives
pushd $RPM_BUILD_ROOT%{_bindir}
for i in cancel lp lpq lpr lprm lpstat; do
	mv $i $i.cups
done
cd $RPM_BUILD_ROOT%{_sbindir}
mv lpc lpc.cups
cd $RPM_BUILD_ROOT%{_mandir}/man1
for i in cancel lp lpq lpr lprm lpstat; do
	mv $i.1 $i-cups.1
done
cd $RPM_BUILD_ROOT%{_mandir}/man8
mv lpc.8 lpc-cups.8
popd
%endif

mkdir -p $RPM_BUILD_ROOT%{_datadir}/pixmaps $RPM_BUILD_ROOT%{_sysconfdir}/X11/sysconfig $RPM_BUILD_ROOT%{_sysconfdir}/X11/applnk/System $RPM_BUILD_ROOT%{_sysconfdir}/xinetd.d $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d $RPM_BUILD_ROOT%{_sysconfdir}/cron.daily
install -c -m 644 %{SOURCE2} $RPM_BUILD_ROOT%{_datadir}/pixmaps
install -c -m 644 cups-lpd.real $RPM_BUILD_ROOT%{_sysconfdir}/xinetd.d/cups-lpd
install -c -m 644 %{SOURCE6} $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/cups
install -c -m 755 %{SOURCE7} $RPM_BUILD_ROOT%{cups_serverbin}/backend/ncp
install -c -m 755 %{SOURCE8} $RPM_BUILD_ROOT%{_sysconfdir}/cron.daily/cups
install -c -m 755 %{SOURCE9} $RPM_BUILD_ROOT%{cups_serverbin}/filter/textonly
install -c -m 644 %{SOURCE10} $RPM_BUILD_ROOT%{_datadir}/cups/model/textonly.ppd

# Ship pstopdf for LSPP systems to deal with malicious postscript
%if %lspp
install -c -m 755 %{SOURCE4} $RPM_BUILD_ROOT%{cups_serverbin}/filter
%endif

# Ship an rpm macro for where to put driver executables.
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/rpm/
install -m 0644 %{SOURCE11} $RPM_BUILD_ROOT%{_sysconfdir}/rpm/

# Ship a printers.conf file, and a client.conf file.  That way, they get
# their SELinux file contexts set correctly.
touch $RPM_BUILD_ROOT%{_sysconfdir}/cups/printers.conf
touch $RPM_BUILD_ROOT%{_sysconfdir}/cups/classes.conf
touch $RPM_BUILD_ROOT%{_sysconfdir}/cups/client.conf
touch $RPM_BUILD_ROOT%{_sysconfdir}/cups/subscriptions.conf

# This is %%ghost'ed, but needs to be created in %%install anyway.
touch $RPM_BUILD_ROOT%{_sysconfdir}/cups/lpoptions

# LSB 3.2 printer driver directory
mkdir -p $RPM_BUILD_ROOT%{_datadir}/ppd

# Remove unshipped files.
rm -rf $RPM_BUILD_ROOT%{_mandir}/cat? $RPM_BUILD_ROOT%{_mandir}/*/cat?
rm -f $RPM_BUILD_ROOT%{_datadir}/applications/cups.desktop
rm -rf $RPM_BUILD_ROOT%{_datadir}/icons

# install /usr/lib/tmpfiles.d/cups.conf (bug #656566)
mkdir -p ${RPM_BUILD_ROOT}%{_prefix}/lib/tmpfiles.d
cat > ${RPM_BUILD_ROOT}%{_prefix}/lib/tmpfiles.d/cups.conf <<EOF
d %{_localstatedir}/run/cups 0755 root lp -
d %{_localstatedir}/run/cups/certs 0511 lp sys -
EOF

# /usr/lib/tmpfiles.d/cups-lp.conf (bug #812641)
cat > ${RPM_BUILD_ROOT}%{_prefix}/lib/tmpfiles.d/cups-lp.conf <<EOF
# This file is part of cups.
#
# Legacy parallel port character device nodes, to trigger the
# auto-loading of the kernel module on access.
#
# See tmpfiles.d(5) for details

c /dev/lp0 0660 root lp - 6:0
c /dev/lp1 0660 root lp - 6:1
c /dev/lp2 0660 root lp - 6:2
c /dev/lp3 0660 root lp - 6:3
EOF

find $RPM_BUILD_ROOT -type f -o -type l | sed '
s:.*\('%{_datadir}'/\)\([^/_]\+\)\(.*\.po$\):%lang(\2) \1\2\3:
/^%lang(C)/d
/^\([^%].*\)/d
' > %{name}.lang

%post
if [ $1 -eq 1 ] ; then
	# Initial installation
	/bin/systemctl enable cups.{service,socket,path} >/dev/null 2>&1 || :
fi

# Remove old-style certs directory; new-style is /var/run
# (see bug #194581 for why this is necessary).
/bin/rm -rf %{_sysconfdir}/cups/certs
%if %use_alternatives
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
rm -f %{_localstatedir}/cache/cups/*.ipp %{_localstatedir}/cache/cups/*.cache
exit 0

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%preun
if [ $1 -eq 0 ] ; then
	# Package removal, not upgrade
	/bin/systemctl --no-reload disable %{name}.path %{name}.socket %{name}.service >/dev/null 2>&1 || :
	/bin/systemctl stop %{name}.path %{name}.socket %{name}.service >/dev/null 2>&1 || :
%if %use_alternatives
	/usr/sbin/alternatives --remove print %{_bindir}/lpr.cups
%endif
fi
exit 0

%postun
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ]; then
	# Package upgrade, not uninstall
	/bin/systemctl try-restart %{name}.service >/dev/null 2>&1 || :
fi
exit 0

%triggerun -- %{name} < 1:1.5.0-22
# This package is allowed to autostart; however, the upgrade trigger
# in Fedora 16 final failed to actually do this.  Do it now as a
# one-off fix for bug #748841.
/bin/systemctl --no-reload enable %{name}.{service,socket,path} >/dev/null 2>&1 || :

%triggerun -- %{name} < 1:1.5-0.9
# Save the current service runlevel info
# User must manually run systemd-sysv-convert --apply cups
# to migrate them to systemd targets
%{_bindir}/systemd-sysv-convert --save %{name} >/dev/null 2>&1 || :

# This package is allowed to autostart:
/bin/systemctl --no-reload enable %{name}.{service,socket,path} >/dev/null 2>&1 || :

# Run these because the SysV package being removed won't do them
/sbin/chkconfig --del cups >/dev/null 2>&1 || :
/bin/systemctl try-restart %{name}.service >/dev/null 2>&1 || :

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
%doc README.txt CREDITS.txt CHANGES.txt
%dir %attr(0755,root,lp) %{_sysconfdir}/cups
%dir %attr(0755,root,lp) %{_localstatedir}/run/cups
%dir %attr(0511,lp,sys) %{_localstatedir}/run/cups/certs
%{_prefix}/lib/tmpfiles.d/cups.conf
%{_prefix}/lib/tmpfiles.d/cups-lp.conf
%verify(not md5 size mtime) %config(noreplace) %attr(0640,root,lp) %{_sysconfdir}/cups/cupsd.conf
%attr(0640,root,lp) %{_sysconfdir}/cups/cupsd.conf.default
%verify(not md5 size mtime) %config(noreplace) %attr(0644,root,lp) %{_sysconfdir}/cups/client.conf
%verify(not md5 size mtime) %config(noreplace) %attr(0600,root,lp) %{_sysconfdir}/cups/classes.conf
%verify(not md5 size mtime) %config(noreplace) %attr(0600,root,lp) %{_sysconfdir}/cups/printers.conf
%verify(not md5 size mtime) %config(noreplace) %attr(0644,root,lp) %{_sysconfdir}/cups/snmp.conf
%verify(not md5 size mtime) %config(noreplace) %attr(0644,root,lp) %{_sysconfdir}/cups/subscriptions.conf
%{_sysconfdir}/cups/interfaces
%verify(not md5 size mtime) %config(noreplace) %attr(0644,root,lp) %{_sysconfdir}/cups/lpoptions
%dir %attr(0755,root,lp) %{_sysconfdir}/cups/ppd
%dir %attr(0700,root,lp) %{_sysconfdir}/cups/ssl
%config(noreplace) %{_sysconfdir}/pam.d/cups
%config(noreplace) %{_sysconfdir}/logrotate.d/cups
%dir %{_datadir}/%{name}/www
%dir %{_datadir}/%{name}/www/es
%dir %{_datadir}/%{name}/www/eu
%dir %{_datadir}/%{name}/www/ja
%dir %{_datadir}/%{name}/www/pl
%dir %{_datadir}/%{name}/www/ru
%{_datadir}/%{name}/www/images
%{_datadir}/%{name}/www/*.css
%doc %{_datadir}/%{name}/www/index.html
%doc %{_datadir}/%{name}/www/help
%doc %{_datadir}/%{name}/www/robots.txt
%doc %{_datadir}/%{name}/www/de/index.html
%doc %{_datadir}/%{name}/www/es/index.html
%doc %{_datadir}/%{name}/www/eu/index.html
%doc %{_datadir}/%{name}/www/fr/index.html
%doc %{_datadir}/%{name}/www/hu/index.html
%doc %{_datadir}/%{name}/www/id/index.html
%doc %{_datadir}/%{name}/www/it/index.html
%doc %{_datadir}/%{name}/www/ja/index.html
%doc %{_datadir}/%{name}/www/pl/index.html
%doc %{_datadir}/%{name}/www/ru/index.html
%{_unitdir}/%{name}.service
%{_unitdir}/%{name}.socket
%{_unitdir}/%{name}.path
%{_bindir}/cupstestppd
%{_bindir}/cupstestdsc
%{_bindir}/cancel*
%{_bindir}/lp*
%{_bindir}/ppd*
%dir %{cups_serverbin}
%{cups_serverbin}/backend
%{cups_serverbin}/cgi-bin
%dir %{cups_serverbin}/daemon
%{cups_serverbin}/daemon/cups-polld
%{cups_serverbin}/daemon/cups-deviced
%{cups_serverbin}/daemon/cups-driverd
%{cups_serverbin}/daemon/cups-exec
%{cups_serverbin}/notifier
%{cups_serverbin}/filter
%{cups_serverbin}/monitor
%{cups_serverbin}/driver
%{_mandir}/man1/cancel*
%{_mandir}/man1/cupstest*
%{_mandir}/man1/lp*
%{_mandir}/man1/ppd*
%{_mandir}/man[578]/*
%{_sbindir}/*
%dir %{_datadir}/cups
%dir %{_datadir}/cups/banners
%{_datadir}/cups/banners/*
%{_datadir}/cups/charsets
%{_datadir}/cups/data
%{_datadir}/cups/fonts
%{_datadir}/cups/model
%dir %{_datadir}/cups/templates
%{_datadir}/cups/templates/*.tmpl
%{_datadir}/cups/templates/de/*.tmpl
%{_datadir}/cups/templates/es/*.tmpl
%{_datadir}/cups/templates/eu/*.tmpl
%{_datadir}/cups/templates/fr/*.tmpl
%{_datadir}/cups/templates/hu/*.tmpl
%{_datadir}/cups/templates/id/*.tmpl
%{_datadir}/cups/templates/it/*.tmpl
%{_datadir}/cups/templates/ja/*.tmpl
%{_datadir}/cups/templates/pl/*.tmpl
%{_datadir}/cups/templates/ru/*.tmpl
%{_datadir}/locale/*/*.po
%{_datadir}/ppd
%dir %attr(1770,root,lp) %{_localstatedir}/spool/cups/tmp
%dir %attr(0710,root,lp) %{_localstatedir}/spool/cups
%dir %attr(0755,lp,sys) %{_localstatedir}/log/cups
%{_datadir}/pixmaps/cupsprinter.png
%{_sysconfdir}/cron.daily/cups
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/cups.conf
%{_datadir}/cups/drv
%{_datadir}/cups/examples
%dir %{_datadir}/cups/mime
%{_datadir}/cups/mime/mime.types
%{_datadir}/cups/mime/mime.convs
%dir %{_datadir}/cups/ppdc
%{_datadir}/cups/ppdc/*.defs
%{_datadir}/cups/ppdc/*.h

%files libs
%doc LICENSE.txt
%{_libdir}/*.so.*

%files devel
%{_bindir}/cups-config
%{_libdir}/*.so
%{_includedir}/cups
%{_mandir}/man1/cups-config.1*
%{_sysconfdir}/rpm/macros.cups

%files lpd
%config(noreplace) %{_sysconfdir}/xinetd.d/cups-lpd
%dir %{cups_serverbin}
%dir %{cups_serverbin}/daemon
%{cups_serverbin}/daemon/cups-lpd

%files ipptool
%{_bindir}/ipptool
%dir %{_datadir}/cups/ipptool
%{_datadir}/cups/ipptool/*
%{_mandir}/man1/ipptool.1.gz

