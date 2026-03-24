#!/bin/bash

# Automated external drive preparation for Linux (Ubuntu/Alpine) use
# - SMART check
# - Badblocks scan (read-only)
# - Format as ext4
# - Repeat for all external drives

set -e

# Find all external disks
EXTERNAL_DISKS=$(diskutil list external | grep '^/dev/' | awk '{print $1}')

for disk in $EXTERNAL_DISKS; do
  echo "============================="
  echo "Processing $disk"
  echo "Unmounting..."
  diskutil unmountDisk $disk || true

  # SMART check
  echo "SMART health for $disk:"
  sudo smartctl -a $disk | grep -E 'Device Model|User Capacity|SMART overall-health|Reallocated_Sector_Ct|Current_Pending_Sector|Offline_Uncorrectable'

  # Badblocks scan (read-only, safe, will take hours for large drives)
  echo "Running badblocks scan on $disk (this may take hours)..."
  sudo /opt/homebrew/opt/e2fsprogs/sbin/badblocks -sv $disk > ~/badblocks_$(basename $disk).txt

  echo "Bad blocks found (if any):"
  cat ~/badblocks_$(basename $disk).txt

  # Format as ext4 (Linux-friendly)
  echo "Formatting $disk as ext4..."
  sudo /opt/homebrew/opt/e2fsprogs/sbin/mkfs.ext4 -F -L jitta_data $disk

  echo "$disk is ready for Linux use."
  echo "============================="

done

echo "All detected external drives processed."
