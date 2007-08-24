Summary:	Status monitor and configuration tool for Epson inkjet printers
Name:		mtink
Version:	1.0.14
Release:	%mkrel 5
License:	GPL
Group:		System/Printing
URL:		http://xwtools.automatix.de/files/
Source0:	http://xwtools.automatix.de/files/%{name}-%{version}.tar.gz
Source1:	mtinkd.init
Source2:	mtinkd.sysconfig
Source3:	printutils.png
# mtink - Do not request koi8-ru, but koi8-r instead. Fixes mdv#25315
Patch0:		mtink-1.0.14-ru_font.patch
Patch1:		mtink-fhs_fixes.diff
Patch2:		mtink-path_to_printer.desc.diff
BuildRequires:	gimp-devel
BuildRequires:	glib-devel
BuildRequires:	gtk2-devel
BuildRequires:	lesstif-devel
BuildRequires:	libgmp-devel
BuildRequires:	libijs-devel
BuildRequires:	jbig-devel
BuildRequires:	lcms-devel
BuildRequires:	libtiff-devel
BuildRequires:	libusb-devel
BuildRequires:	xpm-devel
Requires(post): rpm-helper
Requires(preun): rpm-helper
Conflicts:	printer-utils-2006 printer-utils-2007
Conflicts:	cups-drivers-2006 cups-drivers-2007
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root

%description
Mtink is a status monitor which allow to get the remaining ink quantity,
printing of test patterns, changing and cleaning cartridges.

%prep

%setup -q %{name}-%{version}
%patch0 -p1
%patch1 -p1
%patch2 -p0

cp %{SOURCE1} mtinkd.init
cp %{SOURCE2} mtinkd.sysconfig
cp %{SOURCE3} printutils.png

%build
%serverbuild

perl -p -i -e 's|(/usr/X11R6)/lib\b|\1/%{_lib}|g' Makefile.ORG
perl -p -i -e 's|(/usr)/lib\b|\1/%{_lib}|g' Makefile.ORG
perl -p -i -e 's|(/usr)/lib$|\1/%{_lib}|g' Configure
perl -p -i -e 's|(''/usr/)lib('')|$1%{_lib}$2|g' checkMotifVersion.sh
perl -pi -e "s|^DBG = .*|DBG = $CFLAGS|g" Makefile.ORG

./Configure --no-suid --prefix /usr

%make

# Fix some small bugs
#perl -p -i -e "s/START_LEVEL=S99mtink/START_LEVEL=S59mtink/" etc/installInitScript.sh
#perl -p -i -e "s/STOP_LEVEL=K02mtink/START_LEVEL=K61mtink/" etc/installInitScript.sh
#perl -p -i -e "s/for d in 2 3 4 5/XXXXXXXXXX/" etc/installInitScript.sh
#perl -p -i -e "s/for d in 0 1 6/for d in 2 3 4 5/" etc/installInitScript.sh
#perl -p -i -e "s/XXXXXXXXXX/for d in 0 1 6/" etc/installInitScript.sh
#perl -p -i -e "s!cp mtink /etc/init.d!!" etc/installInitScript.sh
perl -p -i -e "s!chmod 744 /etc/init.d/mtink!!" etc/installInitScript.sh

%install
rm -rf %{buildroot}

install -d %{buildroot}%{_sysconfdir}/sysconfig
install -d %{buildroot}%{_initrddir}
install -d %{buildroot}%{_bindir}
install -d %{buildroot}%{_sbindir}
install -d %{buildroot}%{_libdir}/gimp/2.0/plug-ins
install -d %{buildroot}%{_prefix}/lib/cups/backend
install -d %{buildroot}%{_localstatedir}/mtink
install -d %{buildroot}%{_datadir}/mtink
install -d %{buildroot}/var/run/mtink

install -m0755 mtink %{buildroot}%{_bindir}/
install -m0755 ttink %{buildroot}%{_bindir}/
install -m0755 mtinkc %{buildroot}%{_bindir}/
install -m0755 mtinkd %{buildroot}%{_sbindir}/
install -m0755 mtinkd.init %{buildroot}%{_initrddir}/mtinkd
install -m0644 mtinkd.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/mtinkd

install -m0644 utils/printer.desc.bldin %{buildroot}%{_datadir}/mtink/printer.desc
install -m0644 utils/*.align %{buildroot}%{_datadir}/mtink/

install -m0755 etc/installInitScript.sh %{buildroot}%{_sbindir}/mtink-installInitScript
install -m0755 detect/askPrinter %{buildroot}%{_sbindir}/
install -m0755 etc/mtink-cups %{buildroot}%{_prefix}/lib/cups/backend/mtink
install -m0755 gimp-mtink %{buildroot}%{_libdir}/gimp/2.0/plug-ins/

# Documentation
cp -ax etc/readme README.mtinkd.startup

# Menu entries for printer-utils package
# Menu icon
mkdir -p %{buildroot}%{_datadir}/icons/locolor/16x16/apps/
install -m 644 printutils.png %{buildroot}%{_datadir}/icons/locolor/16x16/apps/
# Menu entries

%if %mdkversion <= 200700
mkdir -p %{buildroot}%{_menudir}
cat <<EOF > %{buildroot}%{_menudir}/printer-utils
?package(printer-utils): \
needs=X11 \
section=Configuration/Printing \
title="Mtink - Epson Inkjet Printer Tools" \
longtitle="Epson inkjet printer maintenance (Head cleaning and alignment, ink level display, cartridge change, ...)" \
command="%{_bindir}/mtink" \
%if %mdkversion == 200700
xdg=true \
%endif
icon="/usr/share/icons/locolor/16x16/apps/printutils.png" \
?package(printer-utils): \
needs=X11 \
section=Applications/Monitoring \
title="Mtink - Epson Inkjet Printer Tools" \
longtitle="Epson inkjet printer maintenance (Head cleaning and alignment, ink level display, cartridge change, ...)" \
command="%{_bindir}/mtink" \
%if %mdkversion == 200700
xdg=true \
%endif
icon="/usr/share/icons/locolor/16x16/apps/printutils.png"
EOF
%endif

%if %mdkversion >= 200700
mkdir -p %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/mandriva-mtink.desktop << EOF
[Desktop Entry]
Encoding=UTF-8
Name=Mtink - Epson Inkjet Printer Tools
Comment=Epson inkjet printer maintenance (Head cleaning and alignment, ink level display, cartridge change, ...)
Exec=%{_bindir}/mtink
Icon=printutils
Terminal=false
Type=Application
%if %mdkversion >= 200800
Categories=System;Monitor;
%else
Categories=X-MandrivaLinux-System-Configuration-Printing;Settings;HardwareSettings;X-MandrivaLinux-System-Monitoring;System;Monitor;
%endif
EOF
%endif

%post
%_post_service mtinkd
# Restart the mtinkd when it is running, but do not activate it by
# default. It blocks the ports for non-Epson devices.
if [ "$1" -ne "1" ]; then
    # On update
    service mtinkd condrestart > /dev/null 2>/dev/null || :
fi
%update_menus

%preun
#Stop mtinkd when uninstalling printer-filters
%_preun_service mtinkd

%postun
if [ "$1" -ge "1" ]; then
    # On update
    /sbin/service mtinkd condrestart >/dev/null 2>&1
fi
%clean_menus

%triggerin -n mtink -- printer-utils-2007
mtinkpid="`pidof mtink`"
if ! [ -z "${mtinkpid}" ]; then
    kill `cat ${mtinkpid}`
    %{_initrddir}/mtinkd start
fi

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc README.mtinkd.startup CHANGE.LOG doc/*
%attr(0755,root,root) %{_initrddir}/mtinkd
%attr(0644,root,sys) %config(noreplace) %{_sysconfdir}/sysconfig/mtinkd
%{_sbindir}/mtinkd
%{_sbindir}/askPrinter
%{_sbindir}/mtink-installInitScript
%attr(0755,root,sys) %{_bindir}/mtinkc
# These four must be SGID sys/SUID root to be able to access the printer
# devices
%attr(6755,root,sys) %{_bindir}/mtink
%attr(6755,root,sys) %{_bindir}/ttink
%attr(2755,lp,sys) %{_libdir}/gimp/2.0/plug-ins/gimp-mtink

%if %mdkversion >= 200700
%{_datadir}/applications/mandriva-mtink.desktop
%endif
%{_datadir}/icons/locolor/16x16/apps/printutils.png
%attr(0750,lp,sys) %dir %{_localstatedir}/mtink
%attr(0750,lp,sys) %dir /var/run/mtink
%attr(0755,root,root) %dir %{_datadir}/mtink
%attr(0644,root,root) %{_datadir}/mtink/*
%attr(0755,root,root) %{_prefix}/lib/cups/backend/mtink
