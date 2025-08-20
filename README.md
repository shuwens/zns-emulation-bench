# zns-emulation-bench

## Start guide

To check all SSD devices, run `lspci -vv | grep NVMe`


## Device under test

We have tested the following three NVMe SSDs.

| Device | Model | Capacity | Description | Read speed (GB/s) | Write speed (GB/s) | Read IOPS | Write IOPS |
|--------|-------|----------|-------------| ----------|-------------|----|---------- |
| Non-ZNS NVMe | Samsung MZ-PLL1T60 | 1.6 TB | Conventional SSD | - | - | 1000k IOPS | 140k IOPS |
| Non-ZNS NVMe | SK hynix Platinum P41/PC801 | 500 GB | Conventional SSD | 7.0 GB/s | 6.8 GB/s | 960k IOPS | 1000k IOPS |
| ZNS NVMe | WD Ultrastar DC ZN540 | 4 TB | ZNS SSD | 3.2 GB/s | 2.0 GB/s | 450k IOPS | 180k IOPS |

They are deployed on the following ZStore nodes:

| Server | SSD model | Number |
|--------|-----------|--------|
| ZStore 2 | ZNS SSD| 2 |
| ZStore 2 | SK SSD| 2 |
| ZStore 3 | ZNS SSD| 2 |
| ZStore 3 | SK SSD| 2 |
| ZStore 6 | Samsung SSD | 2 |


## Results

[grouped bar chart](graphs/1_grouped_bar_chart.pdf)


## FAQ

### Want to bind unmounted NVMe to SPDK but it is already active
See more [here](https://github.com/spdk/spdk/issues/3186), basically you need
to run `blkid` to check the device, and run `dd` on the device so it is not recognized as used device.

```bash
blkid /dev/nvme0n1
```


## Related projects

[NVMeVirt: A Versatile Software-defined Virtual NVMe Device](https://www.usenix.org/conference/fast23/presentation/kim-sang-hoon)
