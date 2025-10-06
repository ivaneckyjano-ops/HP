# Report o stave servera 2025-09-30 16:02 UTC – Conare

- Identifikátor reportu: 1759248164-Conare
- Profil výstupu: MD – Hĺbka stromu: 2 – Limit najväčších súborov: 20

## 1. Zhrnutie

- Stav: OK
- Krátky prehľad: Bez problémov z heuristiky.
- Verejná IP: 64.227.125.155 – Interné IP: pozri sekciu 7
- Upozornenia: viď vyššie

## 2. Systém

- OS: Ubuntu 22.04.5 LTS (kernel: 5.15.0-113-generic)
- Hostname: Conare
- Uptime: up 5 days, 49 minutes
- Čas UTC: 2025-09-30 16:02 UTC
- Virtualizácia: kvm

## 3. Výkon

- Load avg (1/5/15 min): 0.36 0.23 0.09

- CPU info:
  
  ```
  CPU(s):                             1
  Model name:                         DO-Regular
  Thread(s) per core:                 1
  Core(s) per socket:                 1
  Socket(s):                          1
  NUMA node0 CPU(s):                  0
  ```

- CPU jadrá: 1

- RAM / SWAP (free -m):
  
  ```
  total        used        free      shared  buff/cache   available
  Mem:             957         233         109           4         614         553
  Swap:              0           0           0
  ```

## 4. Disky a FS

- Partície (df -h):
  
  ```
  tmpfs          /run          2%   95M
  /dev/vda1      /            16%   21G
  tmpfs          /dev/shm      0%  479M
  tmpfs          /run/lock     0%  5.0M
  /dev/vda15     /boot/efi     6%   99M
  tmpfs          /run/user/0   1%   96M
  ```

- Veľkosti kľúčových priečinkov (du -sh):
  
  ```
  /etc: 5.9M
  /var: 2.0G
  /home: 76K
  /opt: 30M
  /srv: 4.0K
  ```

- Inody:
  
  ```
  tmpfs           122553    716  121837    1% /run
  /dev/vda1      3225600 114877 3110723    4% /
  tmpfs           122553      1  122552    1% /dev/shm
  tmpfs           122553      3  122550    1% /run/lock
  /dev/vda15           0      0       0     - /boot/efi
  tmpfs            24510     26   24484    1% /run/user/0
  ```

## 5. Balíky a aktualizácie

- Správca balíkov: apt
- Nainštalovaných balíkov: 690
- Dostupné aktualizácie: 0

## 6. Služby a procesy

- Bežiace služby (systemd):
  
  ```
  cron.service Regular background program processing daemon
  dbus.service D-Bus System Message Bus
  getty@tty1.service Getty on tty1
  kbagent.service Knowledge‑Base Agent
  multipathd.service Device-Mapper Multipath Device Controller
  networkd-dispatcher.service Dispatcher daemon for systemd-networkd
  nginx.service A high performance web server and a reverse proxy server
  packagekit.service PackageKit Daemon
  polkit.service Authorization Manager
  rsyslog.service System Logging Service
  serial-getty@ttyS0.service Serial Getty on ttyS0
  snapd.service Snap Daemon
  ssh.service OpenBSD Secure Shell server
  systemd-journald.service Journal Service
  systemd-logind.service User Login Management
  systemd-networkd.service Network Configuration
  systemd-resolved.service Network Name Resolution
  systemd-timesyncd.service Network Time Synchronization
  systemd-udevd.service Rule-based Manager for Device Events and Files
  unattended-upgrades.service Unattended Upgrades Shutdown
  user@0.service User Manager for UID 0
  ```

- Počúvajúce porty (ss -tulpn):
  
  ```
  udp   UNCONN 0      0      127.0.0.53%lo:53        0.0.0.0:*    users:(("systemd-resolve",pid=19094,fd=13))                
  tcp   LISTEN 0      511          0.0.0.0:80        0.0.0.0:*    users:(("nginx",pid=249108,fd=8),("nginx",pid=241262,fd=8))
  tcp   LISTEN 0      128          0.0.0.0:22        0.0.0.0:*    users:(("sshd",pid=18874,fd=3))                            
  tcp   LISTEN 0      128          0.0.0.0:8080      0.0.0.0:*    users:(("python",pid=244108,fd=3))                         
  tcp   LISTEN 0      4096   127.0.0.53%lo:53        0.0.0.0:*    users:(("systemd-resolve",pid=19094,fd=14))                
  tcp   LISTEN 0      128             [::]:22           [::]:*    users:(("sshd",pid=18874,fd=4))
  ```

## 7. Sieť

- IP adresy:
  
  ```
  lo               UNKNOWN        127.0.0.1/8 ::1/128 
  eth0             UP             64.227.125.155/20 10.19.0.5/16 fe80::2812:a3ff:fe7b:4aad/64 
  eth1             UP             10.114.0.2/20 fe80::788b:31ff:fe51:6866/64
  ```

- Trasa (default route):
  
  ```
  default via 64.227.112.1 dev eth0 proto static
  ```

- Verejná IP: 64.227.125.155

## 8. Aliasy shellu

```
Aliasy používateľov:
- Používateľ: root
- Používateľ: nobody
- Používateľ: jano
```

## 9. Adresárový strom

- Parametre: hĺbka = 2, vynechané: /proc, /sys, /dev, /run, /var/lib/docker

- /etc:
  
  ```
  /etc
  ├── PackageKit
  ├── X11
  │   ├── Xsession.d
  │   └── xkb
  ├── alternatives
  ├── apache2
  │   └── conf-available
  ├── apparmor
  │   └── init
  ├── apparmor.d
  │   ├── abi
  │   ├── abstractions
  │   ├── disable
  │   ├── force-complain
  │   ├── local
  │   └── tunables
  ├── apport
  │   └── blacklist.d
  ├── apt
  │   ├── apt.conf.d
  │   ├── auth.conf.d
  │   ├── keyrings
  │   ├── preferences.d
  │   ├── sources.list.d
  │   └── trusted.gpg.d
  ├── bash_completion.d
  ├── binfmt.d
  ├── byobu
  ├── ca-certificates
  │   └── update.d
  ├── cloud
  │   ├── clean.d
  │   ├── cloud.cfg.d
  │   └── templates
  ├── console-setup
  ├── cron.d
  ├── cron.daily
  ├── cron.hourly
  ├── cron.monthly
  ├── cron.weekly
  ├── cryptsetup-initramfs
  ├── dbus-1
  │   ├── session.d
  │   └── system.d
  ├── default
  │   └── grub.d
  ├── depmod.d
  ├── dhcp
  │   ├── dhclient-enter-hooks.d
  │   └── dhclient-exit-hooks.d
  ├── dpkg
  │   ├── dpkg.cfg.d
  │   └── origins
  ├── fonts
  │   ├── conf.avail
  │   └── conf.d
  ├── groff
  ├── grub.d
  ├── gss
  │   └── mech.d
  ├── init
  ├── init.d
  ├── initramfs-tools
  │   ├── conf.d
  │   ├── hooks
  │   └── scripts
  ├── iproute2
  │   ├── rt_protos.d
  │   └── rt_tables.d
  ├── iscsi
  ├── kernel
  │   ├── install.d
  │   ├── postinst.d
  │   └── postrm.d
  ├── landscape
  ├── ld.so.conf.d
  ├── ldap
  ├── libblockdev
  │   └── conf.d
  ├── libnl-3
  ├── lighttpd
  │   ├── conf-available
  │   └── conf-enabled
  ├── logcheck
  │   ├── ignore.d.server
  │   └── violations.d
  ├── logrotate.d
  ├── lvm
  │   └── profile
  ├── mdadm
  ├── modprobe.d
  ├── modules-load.d
  ├── multipath
  ├── needrestart
  │   ├── conf.d
  │   ├── hook.d
  │   ├── notify.d
  │   └── restart.d
  ├── netplan
  ├── network
  │   ├── if-pre-up.d
  │   └── if-up.d
  ├── networkd-dispatcher
  │   ├── carrier.d
  │   ├── degraded.d
  │   ├── dormant.d
  │   ├── no-carrier.d
  │   ├── off.d
  │   └── routable.d
  ├── newt
  ├── nginx
  │   ├── conf.d
  │   ├── modules-available
  │   ├── modules-enabled
  │   ├── sites-available
  │   ├── sites-enabled
  │   └── snippets
  ├── opt
  ├── pam.d
  ├── perl
  │   └── Net
  ├── pm
  │   └── sleep.d
  ├── polkit-1
  │   ├── localauthority
  │   └── localauthority.conf.d
  ├── pollinate
  ├── profile.d
  ├── python3
  ├── python3.10
  ├── rc0.d
  ├── rc1.d
  ├── rc2.d
  ├── rc3.d
  ├── rc4.d
  ├── rc5.d
  ├── rc6.d
  ├── rcS.d
  ├── rsyslog.d
  ├── security
  │   ├── limits.d
  │   └── namespace.d
  ├── selinux
  ├── skel
  ├── sos
  │   ├── cleaner
  │   ├── extras.d
  │   ├── groups.d
  │   └── presets.d
  ├── ssh
  │   ├── ssh_config.d
  │   └── sshd_config.d
  ├── ssl
  │   ├── certs
  │   └── private
  ├── sudoers.d
  ├── sysctl.d
  ├── systemd
  │   ├── network
  │   ├── resolved.conf.d
  │   ├── system
  │   └── user
  ├── terminfo
  ├── tmpfiles.d
  ├── ubuntu-advantage
  ├── udev
  │   ├── hwdb.d
  │   └── rules.d
  ├── ufw
  │   └── applications.d
  ├── update-manager
  │   └── release-upgrades.d
  ├── update-motd.d
  ├── update-notifier
  ├── usb_modeswitch.d
  ├── vim
  ├── vmware-tools
  │   ├── scripts
  │   └── vgauth
  └── xdg
    ├── autostart
    └── systemd
  ```

182 directories

```
- /var:
```

/var
├── backups
├── cache
│   ├── PackageKit
│   ├── apparmor
│   ├── apt
│   ├── debconf
│   ├── ldconfig
│   ├── man
│   ├── pollinate
│   ├── private
│   └── snapd
├── crash
├── lib
│   ├── PackageKit
│   ├── apport
│   ├── apt
│   ├── boltd
│   ├── cloud
│   ├── command-not-found
│   ├── dbus
│   ├── dhcp
│   ├── dpkg
│   ├── git
│   ├── grub
│   ├── landscape
│   ├── logrotate
│   ├── man-db
│   ├── misc
│   ├── nginx
│   ├── os-prober
│   ├── pam
│   ├── plymouth
│   ├── polkit-1
│   ├── private
│   ├── python
│   ├── shim-signed
│   ├── snapd
│   ├── sudo
│   ├── system-docs
│   ├── systemd
│   ├── tpm
│   ├── ubuntu-advantage
│   ├── ubuntu-release-upgrader
│   ├── ucf
│   ├── unattended-upgrades
│   ├── update-manager
│   ├── update-notifier
│   ├── usb_modeswitch
│   ├── usbutils
│   └── vim
├── local
├── lock -> /run/lock
├── log
│   ├── apt
│   ├── dist-upgrade
│   ├── journal
│   ├── landscape
│   ├── nginx
│   ├── private
│   ├── server-report
│   └── unattended-upgrades
├── mail
├── opt
├── reports
│   └── server-health
├── run -> /run
├── snap
│   ├── core20
│   ├── core22
│   ├── doctl
│   ├── lxd
│   └── snapd
├── spool
│   ├── cron
│   ├── mail -> ../mail
│   └── rsyslog
├── tmp
│   ├── cloud-init
│   ├── systemd-private-f3ccf9908c66442eae5722e93a4f2694-systemd-logind.service-cy8cbX
│   ├── systemd-private-f3ccf9908c66442eae5722e93a4f2694-systemd-resolved.service-bJ8kbO
│   └── systemd-private-f3ccf9908c66442eae5722e93a4f2694-systemd-timesyncd.service-gKGEhJ
└── www
    └── html

83 directories

```
- /home:
```

/home
├── jano
│   ├── .cache
│   └── .ssh
└── kbagent
    ├── .local
    └── .ssh

6 directories

```
- /opt:
```

/opt
├── kb
│   ├── .git
│   └── venv
├── kbagent
│   └── .ssh
├── server-report
├── status-web-backups
└── system-docs

8 directories

```
- /srv:
```

/srv

0 directories

```
## 10. Súbory
- Najväčšie súbory (top 20):
```

nezistené

```
- Nedávno zmenené (posledných 7 dní):
```

2025-09-30 16:02    /var/log/ufw.log
2025-09-30 16:02    /var/log/syslog
2025-09-30 16:02    /var/log/kern.log
2025-09-30 16:02    /var/log/kbagent.log
2025-09-30 16:02    /var/log/journal/175d072a6f4d0a000f250fc868d55c9b/system.journal
2025-09-30 16:02    /var/log/btmp
2025-09-30 16:02    /var/log/auth.log
2025-09-30 16:02    /opt/kb/.git/FETCH_HEAD
2025-09-30 16:01    /var/www/html/server-reports/Conare/latest.md
2025-09-30 16:01    /var/www/html/server-reports/Conare/latest.html
2025-09-30 16:01    /var/www/html/server-reports/Conare/index.html
2025-09-30 16:01    /var/reports/server-health/2025-09-30-Conare.md
2025-09-30 16:01    /var/lib/apt/periodic/update-success-stamp
2025-09-30 16:01    /var/cache/apt/srcpkgcache.bin
2025-09-30 16:01    /var/cache/apt/pkgcache.bin
2025-09-30 16:00    /var/log/ubuntu-advantage-apt-hook.log
2025-09-30 16:00    /var/log/nginx/ihriska.access.log
2025-09-30 16:00    /var/log/dpkg.log
2025-09-30 16:00    /var/log/apt/term.log
2025-09-30 16:00    /var/log/apt/history.log
2025-09-30 16:00    /var/log/apt/eipp.log.xz
2025-09-30 16:00    /var/lib/update-notifier/updates-available
2025-09-30 16:00    /var/lib/update-notifier/dpkg-run-stamp
2025-09-30 16:00    /var/lib/systemd/timers/stamp-motd-news.timer
2025-09-30 16:00    /var/lib/systemd/timers/stamp-backup-status-web.timer
2025-09-30 16:00    /var/lib/systemd/deb-systemd-helper-enabled/vgauth.service.dsh-also
2025-09-30 16:00    /var/lib/systemd/deb-systemd-helper-enabled/open-vm-tools.service.dsh-also
2025-09-30 16:00    /var/lib/dpkg/triggers/Lock
2025-09-30 16:00    /var/lib/dpkg/status-old
2025-09-30 16:00    /var/lib/dpkg/status
2025-09-30 16:00    /var/lib/dpkg/lock
2025-09-30 16:00    /var/lib/dpkg/info/sosreport.list
2025-09-30 16:00    /var/lib/dpkg/info/python3-packaging.list
2025-09-30 16:00    /var/lib/dpkg/info/open-vm-tools.list
2025-09-30 16:00    /var/lib/apt/extended_states
2025-09-30 16:00    /var/cache/man/index.db
2025-09-30 16:00    /var/cache/ldconfig/aux-cache
2025-09-30 16:00    /var/cache/debconf/templates.dat
2025-09-30 16:00    /var/cache/debconf/config.dat
2025-09-30 16:00    /etc/ld.so.cache
2025-09-30 15:58    /var/lib/ubuntu-advantage/apt-esm/var/cache/apt/srcpkgcache.bin
2025-09-30 15:58    /var/lib/ubuntu-advantage/apt-esm/var/cache/apt/pkgcache.bin
2025-09-30 15:58    /var/lib/dpkg/info/libonig5:amd64.list
2025-09-30 15:58    /var/lib/dpkg/info/libjq1:amd64.list
2025-09-30 15:58    /var/lib/dpkg/info/jq.list
2025-09-30 15:58    /var/cache/debconf/templates.dat-old
2025-09-30 15:58    /var/cache/debconf/config.dat-old
2025-09-30 15:53    /opt/server-report/report.py
2025-09-30 15:46    /var/lib/systemd/timesync/clock
2025-09-30 15:38    /opt/server-report/config.yaml

```
- Zlomené symlinky (max 100):
```

nezistené

```
## 11. Logy
- dmesg (ERR/WARN):
```

[434571.953691] [UFW BLOCK] IN=eth0 OUT= MAC=2a:12:a3:7b:4a:ad:fe:00:00:00:01:01:08:00 SRC=199.21.149.66 DST=64.227.125.155 LEN=40 TOS=0x08 PREC=0x20 TTL=240 ID=14611 PROTO=TCP SPT=41447 DPT=32374 WINDOW=1024 RES=0x00 SYN URGP=0 
[434586.739679] [UFW BLOCK] IN=eth0 OUT= MAC=2a:12:a3:7b:4a:ad:fe:00:00:00:01:01:08:00 SRC=109.205.211.182 DST=64.227.125.155 LEN=40 TOS=0x00 PREC=0x40 TTL=246 ID=11803 PROTO=TCP SPT=51502 DPT=35908 WINDOW=1024 RES=0x00 SYN URGP=0 
[434606.371437] [UFW BLOCK] IN=eth0 OUT= MAC=2a:12:a3:7b:4a:ad:fe:00:00:00:01:01:08:00 SRC=173.255.221.22 DST=64.227.125.155 LEN=44 TOS=0x00 PREC=0x00 TTL=239 ID=54321 PROTO=TCP SPT=47208 DPT=8002 WINDOW=65535 RES=0x00 SYN URGP=0 
[434626.125639] [UFW BLOCK] IN=eth0 OUT= MAC=2a:12:a3:7b:4a:ad:fe:00:00:00:01:01:08:00 SRC=162.216.150.195 DST=10.19.0.5 LEN=44 TOS=0x00 PREC=0x60 TTL=248 ID=232 PROTO=TCP SPT=51459 DPT=3139 WINDOW=1024 RES=0x00 SYN URGP=0 
[434648.399180] [UFW BLOCK] IN=eth0 OUT= MAC=2a:12:a3:7b:4a:ad:fe:00:00:00:01:01:08:00 SRC=109.205.211.182 DST=64.227.125.155 LEN=40 TOS=0x00 PREC=0x40 TTL=246 ID=33258 PROTO=TCP SPT=51502 DPT=38959 WINDOW=1024 RES=0x00 SYN URGP=0 
[434666.589766] [UFW BLOCK] IN=eth0 OUT= MAC=2a:12:a3:7b:4a:ad:fe:00:00:00:01:01:08:00 SRC=109.205.211.182 DST=64.227.125.155 LEN=40 TOS=0x00 PREC=0x40 TTL=246 ID=52503 PROTO=TCP SPT=51502 DPT=33510 WINDOW=1024 RES=0x00 SYN URGP=0 
[434690.038921] [UFW BLOCK] IN=eth0 OUT= MAC=2a:12:a3:7b:4a:ad:fe:00:00:00:01:01:08:00 SRC=103.48.81.36 DST=64.227.125.155 LEN=40 TOS=0x00 PREC=0x00 TTL=239 ID=48374 PROTO=TCP SPT=42006 DPT=8689 WINDOW=1024 RES=0x00 SYN URGP=0 
[434706.331732] [UFW BLOCK] IN=eth0 OUT= MAC=2a:12:a3:7b:4a:ad:fe:00:00:00:01:01:08:00 SRC=104.255.154.159 DST=64.227.125.155 LEN=40 TOS=0x08 PREC=0x20 TTL=243 ID=53468 PROTO=TCP SPT=41418 DPT=18175 WINDOW=1024 RES=0x00 SYN URGP=0 
[434726.523555] [UFW BLOCK] IN=eth0 OUT= MAC=2a:12:a3:7b:4a:ad:fe:00:00:00:01:01:08:00 SRC=79.124.62.53 DST=64.227.125.155 LEN=40 TOS=0x08 PREC=0x20 TTL=246 ID=52856 PROTO=TCP SPT=50359 DPT=3389 WINDOW=1024 RES=0x00 SYN URGP=0 
[434746.250533] [UFW BLOCK] IN=eth0 OUT= MAC=2a:12:a3:7b:4a:ad:fe:00:00:00:01:01:08:00 SRC=103.48.81.36 DST=64.227.125.155 LEN=40 TOS=0x00 PREC=0x00 TTL=239 ID=48985 PROTO=TCP SPT=42006 DPT=6049 WINDOW=1024 RES=0x00 SYN URGP=0 
[434766.472780] [UFW BLOCK] IN=eth0 OUT= MAC=2a:12:a3:7b:4a:ad:fe:00:00:00:01:01:08:00 SRC=109.205.211.162 DST=10.19.0.5 LEN=40 TOS=0x00 PREC=0x40 TTL=246 ID=18705 PROTO=TCP SPT=51418 DPT=25172 WINDOW=1024 RES=0x00 SYN URGP=0 
[434786.237404] [UFW BLOCK] IN=eth0 OUT= MAC=2a:12:a3:7b:4a:ad:fe:00:00:00:01:01:08:00 SRC=109.205.211.162 DST=10.19.0.5 LEN=40 TOS=0x00 PREC=0x40 TTL=246 ID=7039 PROTO=TCP SPT=51418 DPT=24976 WINDOW=1024 RES=0x00 SYN URGP=0 
[434806.911758] [UFW BLOCK] IN=eth0 OUT= MAC=2a:12:a3:7b:4a:ad:fe:00:00:00:01:01:08:00 SRC=104.255.152.19 DST=64.227.125.155 LEN=40 TOS=0x08 PREC=0x20 TTL=243 ID=63290 PROTO=TCP SPT=41411 DPT=14150 WINDOW=1024 RES=0x00 SYN URGP=0 
[434834.742016] [UFW BLOCK] IN=eth0 OUT= MAC=2a:12:a3:7b:4a:ad:fe:00:00:00:01:01:08:00 SRC=104.255.152.29 DST=64.227.125.155 LEN=40 TOS=0x08 PREC=0x20 TTL=243 ID=37611 PROTO=TCP SPT=41404 DPT=12110 WINDOW=1024 RES=0x00 SYN URGP=0 
[434847.325583] [UFW BLOCK] IN=eth0 OUT= MAC=2a:12:a3:7b:4a:ad:fe:00:00:00:01:01:08:00 SRC=104.255.152.19 DST=64.227.125.155 LEN=40 TOS=0x08 PREC=0x20 TTL=243 ID=8307 PROTO=TCP SPT=41411 DPT=15987 WINDOW=1024 RES=0x00 SYN URGP=0 
[434868.155857] [UFW BLOCK] IN=eth0 OUT= MAC=2a:12:a3:7b:4a:ad:fe:00:00:00:01:01:08:00 SRC=143.42.1.53 DST=10.19.0.5 LEN=44 TOS=0x00 PREC=0x00 TTL=240 ID=54321 PROTO=TCP SPT=58906 DPT=4506 WINDOW=65535 RES=0x00 SYN URGP=0 
[434888.743308] [UFW BLOCK] IN=eth0 OUT= MAC=2a:12:a3:7b:4a:ad:fe:00:00:00:01:01:08:00 SRC=104.255.154.159 DST=64.227.125.155 LEN=40 TOS=0x08 PREC=0x20 TTL=243 ID=4015 PROTO=TCP SPT=41418 DPT=17453 WINDOW=1024 RES=0x00 SYN URGP=0 
[434906.515628] [UFW BLOCK] IN=eth0 OUT= MAC=2a:12:a3:7b:4a:ad:fe:00:00:00:01:01:08:00 SRC=162.216.149.149 DST=10.19.0.5 LEN=44 TOS=0x00 PREC=0x60 TTL=248 ID=5522 PROTO=TCP SPT=55970 DPT=23887 WINDOW=1024 RES=0x00 SYN URGP=0 
[434926.396888] [UFW BLOCK] IN=eth0 OUT= MAC=2a:12:a3:7b:4a:ad:fe:00:00:00:01:01:08:00 SRC=109.205.211.162 DST=10.19.0.5 LEN=40 TOS=0x00 PREC=0x40 TTL=246 ID=7894 PROTO=TCP SPT=51418 DPT=29957 WINDOW=1024 RES=0x00 SYN URGP=0 
[434948.021611] [UFW BLOCK] IN=eth0 OUT= MAC=2a:12:a3:7b:4a:ad:fe:00:00:00:01:01:08:00 SRC=104.255.152.18 DST=64.227.125.155 LEN=40 TOS=0x08 PREC=0x20 TTL=243 ID=42012 PROTO=TCP SPT=41363 DPT=1278 WINDOW=1024 RES=0x00 SYN URGP=0

```
- systemd journal (posledných záznamov):
```

Sep 30 16:01:42 Conare systemd[1]: status-web.service: Failed with result 'exit-code'.
Sep 30 16:01:42 Conare systemd[1]: ui-agent.service: Failed with result 'exit-code'.
Sep 30 16:01:45 Conare systemd[255507]: droplet-agent.service: Failed at step EXEC spawning /opt/digitalocean/bin/droplet-agent: No such file or directory
Sep 30 16:01:45 Conare systemd[1]: droplet-agent.service: Failed with result 'exit-code'.
Sep 30 16:01:47 Conare systemd[255509]: status-web.service: Failed at step EXEC spawning /opt/status-web/venv/bin/gunicorn: No such file or directory
Sep 30 16:01:47 Conare systemd[1]: status-web.service: Failed with result 'exit-code'.
Sep 30 16:01:47 Conare systemd[1]: ui-agent.service: Failed with result 'exit-code'.
Sep 30 16:01:48 Conare kernel: [UFW BLOCK] IN=eth0 OUT= MAC=2a:12:a3:7b:4a:ad:fe:00:00:00:01:01:08:00 SRC=162.216.149.149 DST=10.19.0.5 LEN=44 TOS=0x00 PREC=0x60 TTL=248 ID=5522 PROTO=TCP SPT=55970 DPT=23887 WINDOW=1024 RES=0x00 SYN URGP=0 
Sep 30 16:01:52 Conare systemd[255930]: status-web.service: Failed at step EXEC spawning /opt/status-web/venv/bin/gunicorn: No such file or directory
Sep 30 16:01:52 Conare systemd[1]: status-web.service: Failed with result 'exit-code'.
Sep 30 16:01:52 Conare systemd[1]: ui-agent.service: Failed with result 'exit-code'.
Sep 30 16:01:56 Conare systemd[255940]: droplet-agent.service: Failed at step EXEC spawning /opt/digitalocean/bin/droplet-agent: No such file or directory
Sep 30 16:01:56 Conare systemd[1]: droplet-agent.service: Failed with result 'exit-code'.
Sep 30 16:01:57 Conare systemd[255941]: status-web.service: Failed at step EXEC spawning /opt/status-web/venv/bin/gunicorn: No such file or directory
Sep 30 16:01:57 Conare systemd[1]: status-web.service: Failed with result 'exit-code'.
Sep 30 16:01:57 Conare systemd[1]: ui-agent.service: Failed with result 'exit-code'.
Sep 30 16:02:03 Conare systemd[255945]: status-web.service: Failed at step EXEC spawning /opt/status-web/venv/bin/gunicorn: No such file or directory
Sep 30 16:02:03 Conare systemd[1]: status-web.service: Failed with result 'exit-code'.
Sep 30 16:02:03 Conare systemd[1]: ui-agent.service: Failed with result 'exit-code'.
Sep 30 16:02:06 Conare systemd[255949]: droplet-agent.service: Failed at step EXEC spawning /opt/digitalocean/bin/droplet-agent: No such file or directory
Sep 30 16:02:06 Conare systemd[1]: droplet-agent.service: Failed with result 'exit-code'.
Sep 30 16:02:08 Conare kernel: [UFW BLOCK] IN=eth0 OUT= MAC=2a:12:a3:7b:4a:ad:fe:00:00:00:01:01:08:00 SRC=109.205.211.162 DST=10.19.0.5 LEN=40 TOS=0x00 PREC=0x40 TTL=246 ID=7894 PROTO=TCP SPT=51418 DPT=29957 WINDOW=1024 RES=0x00 SYN URGP=0 
Sep 30 16:02:08 Conare systemd[255950]: status-web.service: Failed at step EXEC spawning /opt/status-web/venv/bin/gunicorn: No such file or directory
Sep 30 16:02:08 Conare systemd[1]: status-web.service: Failed with result 'exit-code'.
Sep 30 16:02:08 Conare systemd[1]: ui-agent.service: Failed with result 'exit-code'.
Sep 30 16:02:13 Conare systemd[255952]: status-web.service: Failed at step EXEC spawning /opt/status-web/venv/bin/gunicorn: No such file or directory
Sep 30 16:02:13 Conare systemd[1]: status-web.service: Failed with result 'exit-code'.
Sep 30 16:02:13 Conare systemd[1]: ui-agent.service: Failed with result 'exit-code'.
Sep 30 16:02:16 Conare systemd[255954]: droplet-agent.service: Failed at step EXEC spawning /opt/digitalocean/bin/droplet-agent: No such file or directory
Sep 30 16:02:16 Conare systemd[1]: droplet-agent.service: Failed with result 'exit-code'.
Sep 30 16:02:18 Conare systemd[255955]: status-web.service: Failed at step EXEC spawning /opt/status-web/venv/bin/gunicorn: No such file or directory
Sep 30 16:02:18 Conare systemd[1]: status-web.service: Failed with result 'exit-code'.
Sep 30 16:02:18 Conare systemd[1]: ui-agent.service: Failed with result 'exit-code'.
Sep 30 16:02:24 Conare systemd[255957]: status-web.service: Failed at step EXEC spawning /opt/status-web/venv/bin/gunicorn: No such file or directory
Sep 30 16:02:24 Conare systemd[1]: status-web.service: Failed with result 'exit-code'.
Sep 30 16:02:24 Conare systemd[1]: ui-agent.service: Failed with result 'exit-code'.
Sep 30 16:02:26 Conare systemd[255961]: droplet-agent.service: Failed at step EXEC spawning /opt/digitalocean/bin/droplet-agent: No such file or directory
Sep 30 16:02:26 Conare systemd[1]: droplet-agent.service: Failed with result 'exit-code'.
Sep 30 16:02:29 Conare systemd[255964]: status-web.service: Failed at step EXEC spawning /opt/status-web/venv/bin/gunicorn: No such file or directory
Sep 30 16:02:29 Conare systemd[1]: status-web.service: Failed with result 'exit-code'.
Sep 30 16:02:29 Conare systemd[1]: ui-agent.service: Failed with result 'exit-code'.
Sep 30 16:02:29 Conare kernel: [UFW BLOCK] IN=eth0 OUT= MAC=2a:12:a3:7b:4a:ad:fe:00:00:00:01:01:08:00 SRC=104.255.152.18 DST=64.227.125.155 LEN=40 TOS=0x08 PREC=0x20 TTL=243 ID=42012 PROTO=TCP SPT=41363 DPT=1278 WINDOW=1024 RES=0x00 SYN URGP=0 
Sep 30 16:02:34 Conare systemd[255972]: status-web.service: Failed at step EXEC spawning /opt/status-web/venv/bin/gunicorn: No such file or directory
Sep 30 16:02:34 Conare systemd[1]: status-web.service: Failed with result 'exit-code'.
Sep 30 16:02:34 Conare systemd[1]: ui-agent.service: Failed with result 'exit-code'.
Sep 30 16:02:36 Conare systemd[255976]: droplet-agent.service: Failed at step EXEC spawning /opt/digitalocean/bin/droplet-agent: No such file or directory
Sep 30 16:02:36 Conare systemd[1]: droplet-agent.service: Failed with result 'exit-code'.
Sep 30 16:02:39 Conare systemd[255977]: status-web.service: Failed at step EXEC spawning /opt/status-web/venv/bin/gunicorn: No such file or directory
Sep 30 16:02:39 Conare systemd[1]: status-web.service: Failed with result 'exit-code'.
Sep 30 16:02:39 Conare systemd[1]: ui-agent.service: Failed with result 'exit-code'.

```

## 12. Meta

- Verzia nástroja: 1.2.0
- Konfigurácia: SCAN_DIRS=/etc,/var,/home,/opt,/srv; TREE_DEPTH=2; EXCLUDE_PATHS=/proc,/sys,/dev,/run,/var/lib/docker
- Výstupný adresár: /var/reports/server-health