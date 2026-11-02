#!/bin/bash

# Project configuration
PROJECT_NAME="NetOps-Pro"

# Monitoring configuration
DISK_WARNING=70
DISK_CRITICAL=80

# Collect system information
HOSTNAME_VALUE=$(hostname)
CURRENT_USER=$(whoami)
UPTIME_VALUE=$(uptime -p)

MEMORY_INFO=$(free -h)
DISK_INFO=$(df -h /)

# Extract disk usage percentage
DISK_USAGE=$(df -P / | awk 'NR==2 {
    gsub(/%/, "", $5)
    print $5
}')

# Display server information
echo "======================================"
echo "          $PROJECT_NAME"
echo "          SERVER HEALTH CHECK"
echo "======================================"

echo "Hostname: $HOSTNAME_VALUE"
echo "User: $CURRENT_USER"
echo "Uptime: $UPTIME_VALUE"

echo
echo "========== MEMORY INFORMATION =========="
echo "$MEMORY_INFO"

echo
echo "========== DISK INFORMATION =========="
echo "$DISK_INFO"

echo
echo "========== DISK HEALTH STATUS =========="

# Conditional monitoring
if [ "$DISK_USAGE" -ge "$DISK_CRITICAL" ]; then

    echo "CRITICAL: Disk usage is ${DISK_USAGE}%"

elif [ "$DISK_USAGE" -ge "$DISK_WARNING" ]; then

    echo "WARNING: Disk usage is ${DISK_USAGE}%"

else

    echo "HEALTHY: Disk usage is ${DISK_USAGE}%"

fi

echo "======================================"
