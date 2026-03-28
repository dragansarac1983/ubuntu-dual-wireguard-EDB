## Upustvo za instalaciju i podesavanje​
>Instalacija wiregurad-a
```
sudo apt-get install wireguard
```
Napraviti config fajlove za wireguard dual VPN (dva fajla na dva rutera)
sudo nano /etc/wireguard/wg0.conf
sudo nano /etc/wireguard/wg1.conf

U konfiguracionim fajlovima su komentari na svakoj liniji koda, ispod je primjer sa pojasnjenjem

[Interface]
ListenPort = 39040
PrivateKey = kreirati na AUTO na Peers na Mikrotiku
Address = IP interfejsa na klijentu
DNS = DNS koji treba klijent da koristi

[Peer]
PublicKey = Sa Mikrotik interfejsa
AllowedIPs =Mreze koje treba da dohvati sa Mikrotika
Endpoint = IP Mikrotika
PersistentKeepalive = 10


Iskljucicemo automacko dodavanje ruta u konfigu
Table = off

Definisamo sa PostUP i PostDown koje rute oglasavamo posto cemo mrezu 172.16.250.0/24 oglasavati kroz 2 tunela sa razlicitim metrikama

Kada ubacimo fajlove potrebno je podici tunele

sudo wg-quick up wg0
sudo wg-quick up wg1

Pregled ruta kada se tuneli konektuju
╰─○ ip route
default via 172.16.0.81 dev ens34 proto static
172.16.0.80/29 dev ens34 proto kernel scope link src 172.16.0.84
172.16.10.0/24 dev wg0 scope link
172.16.20.0/24 dev wg1 scope link
172.16.250.0/24 dev wg0 scope link metric 100
172.16.250.0/24 dev wg1 scope link metric 200

Kada je sve uredu potrebno je ove VPN ove iskonfigurisati  da se podizu automacki prilikom podizanja OS-a
sudo systemctl enable wg-quick@wg0.service
sudo systemctl enable wg-quick@wg1.service
sudo systemctl daemon-reload

Kada restartujemo OS VPN ovi treba da su aktivni, mozemo testirati konektivnost

Sledeci problem kojeg rijesavamo je dostupnost mreze koja ima razlicite metrike:

172.16.250.0/24 dev wg0 scope link metric 100
172.16.250.0/24 dev wg1 scope link metric 200

Naime problem je kada wg0 tunel ispadne, da OS drzi tunel UP i saobracaj ide primarnom putanjom, a ne backup koja ce raditi prilikom ispada. Prilikom ispada potrebno je ugasiti tunel wg0 "wg-quick down wg0" i za to cemo koristiti wg-failover.sh koja prati interface na ruteru kroz wireguard tunel wg0 i to 172.16.10.1, znaci ako da putanja ispadne (prati se 5 ispada) i pokrece svakih 120 sekundi tj sleep vrijednost u skripti. Kada se desi ta promjena ova skripta ce pokrenuti i send-warn-mail.py skriptu koja ce poslati mail obavjestenje.
Obadvije skripte se nalaze na lokaciji /usr/local/bin i potrebno ih je kreirati i datim prava za izvrsavanje:

nano /usr/local/bin/wg-failover.sh
sudo chmod +x /usr/local/bin/wg-failover.sh

nano /usr/local/bin/send-warn-mail.py
sudo chmod +x /usr/local/bin/send-warn-mail.py

ls -la (moraju biti zelene)

Ovu skriptu treba podesiti da se akvira kao servisi kada se racuna restartuje, potrebno je napraviti fajl

nano /etc/systemd/system/wg-failover.service

# Učitaj novi servis
sudo systemctl daemon-reexec
sudo systemctl daemon-reload

# Enable (da se pokreće i posle reboota)
sudo systemctl enable wg-failover.service

# Startuj
sudo systemctl start wg-failover.service


# Da li servis radi
sudo systemctl status wg-failover.service

# Logovi iz skripte
sudo journalctl -u wg-failover.service -f

Testirati nakog restarta.

Kada se desi ispad wg0 tunela, potrebno je rucno uci i podici ga na wg-quick up wg0











