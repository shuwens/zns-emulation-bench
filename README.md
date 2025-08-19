# zns-emulation-bench


## Device under test


| Device | Model | Capacity | Description | Read speed (GB/s) | Write speed (GB/s) | Read IOPS | Write IOPS |
|--------|-------|----------|-------------| ----------|-------------|----|---------- |
| Non-ZNS NVMe | Samsung MZ-PLL1T60 | 1.6 TB | Conventional SSD | 6.5 GB/s | 4.5 GB/s | 150k IOPS | 100k IOPS |
| Non-ZNS NVMe | SK hynix Platinum P41/PC801 | 500 GB | Conventional SSD | 7.0 GB/s | 6.8 GB/s | 960k IOPS | 1000k IOPS |
| ZNS NVMe | WD Ultrastar DC ZN540 | 4 TB | ZNS SSD | 3.2 GB/s | 2.0 GB/s | 450k IOPS | 180k IOPS |



## Related projects

[NVMeVirt: A Versatile Software-defined Virtual NVMe Device](https://www.usenix.org/conference/fast23/presentation/kim-sang-hoon)
