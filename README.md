# FlightSize

This repository contains the source code and experiment scripts for paper "Accuracy Evaluation of TCP FlightSize Estimation: Analytical and Experimental Study" published in ICNC 2025. 

## Instructions
On Ubuntu 20.04

```
sudo sysctl -w net.ipv4.ip_forward=1
```

### Install build dependencies
```
sudo apt-get update; sudo apt-get install git fakeroot build-essential ncurses-dev xz-utils libssl-dev bc flex libelf-dev bison zstd dwarves vim git iperf3
```
### Download Linux kernel source code

1. Clone the source code tree
```
git clone git://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
cd linux
```

2. Switch to 5.16 version
(5.16 is the up-to-the-date version when I start this project)

```
git checkout v5.16
```

3. Apply patch ```0001-Patch-for-FlightSize.patch``` to the Linux code repo
```
cp ../FlightSize/Kernel_files/As_patch/0001-Patch-for-FlightSize.patch 0001-Patch-for-FlightSize.patch
git apply 0001-Patch-for-FlightSize.patch
```

### Adjust kernel config

1. Copy compile config file from current system
```
cp /boot/config-$(uname -r) .config
scripts/config --disable SYSTEM_REVOCATION_KEYS
scripts/config --disable SYSTEM_TRUSTED_KEYS
scripts/config --disable CONFIG_MODULE_SIG_ALL
scripts/config --disable CONFIG_MODULE_SIG_KEY
```

2. Enlarge the kernel ring buffer size

```
vim .config
```

change the line to ```CONFIG_LOG_BUF_SHIFT=25``` (otherwise the default ring buffer is not enough for our printk logging)

3. Load make config
```
sudo make menuconfig
```

### Make new kernel

1. Build new kernel with version
```
make deb-pkg clean LOCALVERSION=custominfo
```
This step requires about 50GB free disk space and cost about an hour

2. Insall the kernel in deb format

```
sudo dpkg -i linux-headers-*.deb
sudo dpkg -i linux-image-5.16.0custominfo_*.deb
reboot
```

3. Remove steps

After finish experiments, use ```sudo dpkg -r xxxx``` to remove packets contains 5.16, then reboot


### Install other dependencies

1. Install Mininet
```
git clone https://github.com/mininet/mininet
cd mininet
git checkout -b mininet-2.3.0 2.3.0
cd ..
sudo PYTHON=python3 mininet/util/install.sh -a
```

2. Install python packages

```
sudo pip3 install pandas matplotlib
```

### Adjust script config

Change ROOTDIR and USER in Mininet_testbed/utils/config.py accordingly.


### Run script

```
sudo python3 compare_two_methods.py
```

## Reproduce results

1. Impact of RTT and Bandwidth
```
sudo python3 compare_two_methods.py
```

2. Impact of Packet loss
```
sudo python3 compare_two_methods_loss.py
```

3. Impact of Packet reordering
```
sudo python3 compare_two_methods_reorder.py
```

4. Dynamic emulation
   
The scripts to adjust tc netem is original from [https://github.com/akamai/cell-emulation-util](https://github.com/akamai/cell-emulation-util)

I appreciated their work and adjusted the NIC name to fit the condition.

```
sudo python3 dynamich3.py
```

## Results

[Link](https://drive.google.com/file/d/1o2HjVGSpvqCsrQsXlSFoByF36qF4rj9y/view?usp=sharing) to Google Drive.

## license

GPL-2.0

This work containes Linux code that is ```GPL-2.0-only```
