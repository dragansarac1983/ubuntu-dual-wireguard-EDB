#!/usr/bin/env python3

import smtplib
from datetime import datetime
from email.mime.text import MIMEText
import sys

# <- OVDE PROMENI NA SVOJ APP PASSWORD -> ********************************
APP_PASS = "xxxx hdqu qrjt xxxx"  # Ovde stavi svoj Google App Password
MAIL_FROM = "mm7767081@gmail.com"
MAIL_TO   = "dragansar@gmail.com"
# <- OVDE KRAJ -> ********************************************************

def send_mail(subject, body):
    msg = MIMEText(body)
    msg["From"]    = MAIL_FROM
    msg["To"]      = MAIL_TO
    msg["Subject"] = subject

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(MAIL_FROM, APP_PASS)
        server.sendmail(MAIL_FROM, [MAIL_TO], msg.as_string())
        server.quit()
        print("Mail poslat.")
    except Exception as e:
        print("Greska pri slanju maila:", str(e))

if __name__ == "__main__":
    # hard‑kodiran subject i body, bez potrebe za args
    subject = "EDB Pale SKADA-1 wireguard down"
    body    = f"Doslo je do prekida EDB Pale SKADA-1 wireguard rutera: {str(datetime.now())} - automatska notifikacija"

    send_mail(subject, body)