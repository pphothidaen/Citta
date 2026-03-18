# Hardware & Storage Asset Register

## Purpose
บันทึกทรัพยากรฮาร์ดแวร์และสื่อบันทึกข้อมูลที่มีอยู่จริง ณ ปัจจุบัน เพื่อใช้เป็น baseline ของการออกแบบระบบ Citta

## Core Nodes
| Node      | Details |
|-----------|---------|
| Node 1   | MacBook Pro M4 + Hagibis Dock + ADATA NVMe 2TB |
| Node 2   | Synology DS224+ with 2GB onboard DDR4 non-ECC + 16GB added RAM, Dual LAN, Seagate Exos 8TB x2 |
| Node 3   | DIY J1900 NAS with RAM 8GB and Advantech mSATA SSD 256GB |
| Node 4   | Huawei Y9 2018 x2 with no monitor, no battery, direct USB-A |
| Node 5   | Lenovo ThinkCentre M720q with Intel i5-8500T, RAM 32GB, internal SATA SSD 256GB |

## Network & Backup
- UniFi Switch 8 60W PoE  
- External HDD 1TB USB 3.0  

## Assigned Storage Assets
- ADATA NVMe 2TB -> Node 1  
- Seagate Exos 8TB x2 -> Node 2  
- Advantech mSATA SSD 256GB -> Node 3  
- Lenovo internal SATA SSD 256GB -> Node 5  

## Unassigned / Auxiliary Storage Assets
- HGST 1TB 7200RPM 2.5 SATA HDD  
- Seagate Mobile HDD 1TB ST1000LM035  
- KINGMAX SMV32 120GB SATA SSD  
- WD portable external ~1TB  
- WD desktop external WD3200H1U-00 320GB  
- Schneider dual-head USB flash 16GB  

## Data Tier Classification
| Tier   | Asset(s) |
|--------|----------|
| Hot    | -        |
| Warm   | -        |
| Cold   | -        |
| Offline | -        |

## Notes and Constraints
- Unassigned storage must not be assumed attached to production nodes until physically verified.
