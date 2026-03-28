## Upustvo za instalaciju i podesavanje​
>Instalacija wiregurad-a
```bash
sudo apt-get install wireguard
```
Napraviti config fajlove za wireguard dual VPN (dva fajla na dva rutera)
```bash
sudo nano /etc/wireguard/wg0.conf
```
```bash
sudo nano /etc/wireguard/wg1.conf
```
U konfiguracionim fajlovima su komentari na svakoj liniji koda, ispod je primjer sa pojasnjenjem
```python
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
```
Iskljucicemo automacko dodavanje ruta u konfigu
Table = off

Definisamo sa PostUP i PostDown koje rute oglasavamo posto cemo mrezu 172.16.250.0/24 oglasavati kroz 2 tunela sa razlicitim metrikama

Kada ubacimo fajlove potrebno je podici tunele
```bash
sudo wg-quick up wg0
```
```bash
sudo wg-quick up wg1
```

Pregled ruta kada se tuneli konektuju
```console
╰─○ ip route
default via 172.16.0.81 dev ens34 proto static
172.16.0.80/29 dev ens34 proto kernel scope link src 172.16.0.84
172.16.10.0/24 dev wg0 scope link
172.16.20.0/24 dev wg1 scope link
172.16.250.0/24 dev wg0 scope link metric 100
172.16.250.0/24 dev wg1 scope link metric 200
```

Kada je sve uredu potrebno je ove VPN ove iskonfigurisati  da se podizu automacki prilikom podizanja OS-a
```bash
sudo systemctl enable wg-quick@wg0.service
```
```bash
sudo systemctl enable wg-quick@wg1.service
```
```bash
sudo systemctl daemon-reload
```

Kada restartujemo OS VPN ovi treba da su aktivni, mozemo testirati konektivnost

Sledeci problem kojeg rijesavamo je dostupnost mreze koja ima razlicite metrike:
```console
172.16.250.0/24 dev wg0 scope link metric 100
172.16.250.0/24 dev wg1 scope link metric 200
```

Naime problem je kada wg0 tunel ispadne, da OS drzi tunel UP i saobracaj ide primarnom putanjom, a ne backup koja ce raditi prilikom ispada. Prilikom ispada potrebno je ugasiti tunel wg0 "wg-quick down wg0" i za to cemo koristiti wg-failover.sh koja prati interface na ruteru kroz wireguard tunel wg0 i to 172.16.10.1, znaci ako da putanja ispadne (prati se 5 ispada) i pokrece svakih 120 sekundi tj sleep vrijednost u skripti. Kada se desi ta promjena ova skripta ce pokrenuti i send-warn-mail.py skriptu koja ce poslati mail obavjestenje.
Obadvije skripte se nalaze na lokaciji /usr/local/bin i potrebno ih je kreirati i datim prava za izvrsavanje:

```bash
nano /usr/local/bin/wg-failover.sh
```
```bash
sudo chmod +x /usr/local/bin/wg-failover.sh
```
```bash
nano /usr/local/bin/send-warn-mail.py
```
```bash
sudo chmod +x /usr/local/bin/send-warn-mail.py
```
Moraju biti zelene posle provjere
```
ls -la
``` 
Ovu skriptu treba podesiti da se akvira kao servisi kada se racuna restartuje, potrebno je napraviti fajl
```bash
nano /etc/systemd/system/wg-failover.service
```
Učitaj novi servis
```bash
sudo systemctl daemon-reexec
```
```bash
sudo systemctl daemon-reload
```
Enable (da se pokreće i posle reboota)
```bash
sudo systemctl enable wg-failover.service
```
Startuj
```bash
sudo systemctl start wg-failover.service
```
Da li servis radi
```bash
sudo systemctl status wg-failover.service
```
Logovi iz skripte
```bash
sudo journalctl -u wg-failover.service -f
```
Testirati nakog restarta.

Kada se desi ispad wg0 tunela, potrebno je rucno uci i podici ga na 
```bash
wg-quick up wg0
```
