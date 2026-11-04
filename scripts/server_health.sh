#!/bin/bash

# Project configuration
PROJECT_NAME="NetOps-Pro"

# Function to calculate CPU utilization

get_cpu_usage() {

    read -r cpu user nice system idle iowait irq softirq steal _ < /proc/stat

    IDLE1=$((idle + iowait))

    TOTAL1=$((user + nice + system + idle + iowait + irq + softirq + steal))

    sleep 1

    read -r cpu user nice system idle iowait irq softirq steal _ < /proc/stat

    IDLE2=$((idle + iowait))

    TOTAL2=$((user + nice + system + idle + iowait + irq + softirq + steal))

    TOTAL_DIFF=$((TOTAL2 - TOTAL1))

    IDLE_DIFF=$((IDLE2 - IDLE1))

    if [ "$TOTAL_DIFF" -gt 0 ]; then

        CPU_USAGE=$(( (TOTAL_DIFF - IDLE_DIFF) * 100 / TOTAL_DIFF ))

    else

        CPU_USAGE=0

    fi

    echo "$CPU_USAGE"
}


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
# CPU monitoring
CPU_USAGE=$(get_cpu_usage)
echo "CPU Usage: ${CPU_USAGE}%"

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

echo
echo "========== CPU HEALTH STATUS =========="

if [ "$CPU_USAGE" -ge 90 ]; then

    echo "CRITICAL: CPU utilization is ${CPU_USAGE}%"

elif [ "$CPU_USAGE" -ge 70 ]; then

    echo "WARNING: CPU utilization is ${CPU_USAGE}%"

else

    echo "HEALTHY: CPU utilization is ${CPU_USAGE}%"

fi

echo
echo "========== SERVICE HEALTH CHECK =========="

# Services to monitor
SERVICES=("ssh" "docker" "cron" "NetworkManager")

# Function to check service status
check_service() {

    SERVICE_NAME=$1

    if systemctl is-active --quiet "$SERVICE_NAME"; then

        echo "[RUNNING] $SERVICE_NAME"

    else

        echo "[NOT RUNNING] $SERVICE_NAME"

    fi
}

# Loop through all services
for SERVICE in "${SERVICES[@]}"
do

    check_service "$SERVICE"

done

echo "======================================"

echo "======================================"
