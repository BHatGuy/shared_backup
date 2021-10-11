# shared backup guide / cheat sheet


## Wireguard

We might have to change the subnet and ports!
Everyone needs his own ip suffix!

Packages: ```wireguard-tools iptables-persistent```

Generate private key: ```(umask 0077; wg genkey > peer_A.key)```

then generate public key: ```wg pubkey < peer_A.key > peer_A.pub```

If we want, we can additionaly use preshared keys: ```wg genpsk > peer_A-peer_B.psk```

```
/etc/wireguard/wg0.conf

[Interface]
Address = 10.10.10.1/24
ListenPort = 51821
PrivateKey = XXXXX

PostUp = iptables -A INPUT -i %i -j wireguard
PostDown = iptables -D INPUT -i %i -j wireguard

[Peer]
PublicKey = XXXXX
PresharedKey = XXXXX
AllowedIPs = 10.10.10.2/32
Endpoint = xxx.xxx.xxx.xxx:51821
```


```
/etc/iptables/rules.v4

*filter
:INPUT ACCEPT [0:0]
:FORWARD ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]
:wireguard - [0:0]
-A wireguard -p tcp -m tcp --sport 22 --dport 1024:65535 -m state --state ESTABLISHED -j ACCEPT
-A wireguard -p tcp -m tcp --sport 1024:65535 --dport 22 -m state --state NEW,ESTABLISHED -j ACCEPT
-A wireguard -j DROP
COMMIT
```

Activate the interface with: ```sudo systemctl enable --now wg-quick@wg0```

Show active wireguard intefaces and peers: ```sudo wg```

Show active iptable rules: ```sudo iptables -nvL```

## ecryptfs / fstab

Mount as a test: ```sudo mount.ecryptfs encrypted/ decrypted/```
then get the entry form ```cat /etc/mtab``` and append it to ```/etc/fstab```
add ```noauto,user``` to the list of options.

Now mounting as user is possible:
First add the key: ```ecryptfs-add-passphrase``` and them mount with ```mount -i decrypted```

Unmount with ```umount decrypted```

## users / ssh 


## cron


## Links
- https://wiki.archlinux.org/title/WireGuard
- https://wiki.archlinux.org/title/ECryptfs