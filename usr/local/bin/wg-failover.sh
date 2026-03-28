#!/bin/bash

WG0_END=172.16.10.1
MAIL_SCRIPT="/usr/local/bin/send-warn-mail.py"
WG0_DOWN=0
ALERT_SENT=0

while true; do
    if ! ping -c 5 -W 5 "$WG0_END" > /dev/null 2>&1; then
        if [ $WG0_DOWN -eq 0 ]; then
            echo "$(date) - WG0 IP $WG0_END nije dostupan, obaram wg0"
            sudo wg-quick down wg0
            WG0_DOWN=1
        fi

        if [ $ALERT_SENT -eq 0 ]; then
            echo "$(date) - Šaljem jednu notifikaciju o padu wg0"
            sudo "$MAIL_SCRIPT"
            ALERT_SENT=1
        fi
    else
        if [ $WG0_DOWN -eq 1 ]; then
            echo "$(date) - WG0 IP $WG0_END je ponovo dostupan"
        fi
        WG0_DOWN=0
        ALERT_SENT=0
    fi

    sleep 120
done
