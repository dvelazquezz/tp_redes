from netmiko import ConnectHandler

# === DISPOSITIVOS ===
devices = {
    "R1": {
        "device_type": "mikrotik_routeros",
        "ip": "10.10.20.1",
        "username": "admin",
        "password": "1234"
    },
    "SW1": {
        "device_type": "cisco_ios",
        "ip": "10.10.20.2",
        "username": "admin",
        "password": "1234"
    },
    "SW2": {
        "device_type": "cisco_ios",
        "ip": "10.10.20.3",
        "username": "admin",
        "password": "1234"
    },
    "R2": {
        "device_type": "mikrotik_routeros",
        "ip": "10.10.20.4",
        "username": "admin",
        "password": "1234"
    }
}

# === CONFIGURACIONES ===

# SW1 – Switch Principal
cfg_sw1 = [
    "vlan 319", "name NATIVA",
    "vlan 2099", "name GESTION",
    "interface Vlan2099",
    " ip address 10.10.20.2 255.255.255.248",
    " no shutdown", "exit",
    "interface Ethernet1/0",
    " switchport mode access",
    " switchport access vlan 2099",
    " no shutdown", "exit",
    "interface Ethernet0/0",
    " switchport trunk encapsulation dot1q",
    " switchport mode trunk",
    " switchport trunk native vlan 319",
    " switchport trunk allowed vlan 319,2099",
    " no shutdown", "exit",
    "ip default-gateway 10.10.20.1"
]

# SW2 – Switch Remoto
cfg_sw2 = [
    "vlan 319", "name NATIVA",
    "vlan 2099", "name GESTION",
    "interface Vlan2099",
    " ip address 10.10.20.3 255.255.255.248",
    " no shutdown", "exit",
    "interface Ethernet0/0",
    " switchport trunk encapsulation dot1q",
    " switchport mode trunk",
    " switchport trunk native vlan 319",
    " switchport trunk allowed vlan 319,2099",
    " no shutdown", "exit",
    "interface Ethernet0/1",
    " switchport mode access",
    " switchport access vlan 2099",
    " no shutdown", "exit",
    "ip default-gateway 10.10.20.1"
]

# R1 – MikroTik Principal
cfg_r1 = [
    "/interface bridge add name=br-core vlan-filtering=yes",
    "/interface bridge port add bridge=br-core interface=ether2 comment='Hacia SW1'",
    "/interface bridge port add bridge=br-core interface=ether3 comment='Hacia R2'",
    "/interface bridge vlan add bridge=br-core vlan-ids=319 untagged=ether2,ether3",
    "/interface bridge vlan add bridge=br-core vlan-ids=2099 tagged=br-core,ether2,ether3",
    "/interface vlan add name=gestion2099 vlan-id=2099 interface=br-core",
    "/ip address add address=10.10.20.1/29 interface=gestion2099",
    "/ip service set ssh disabled=no",
    "/ip service set telnet disabled=yes",
    "/ip service set ftp disabled=yes",
    "/ip service set www disabled=yes",
    "/system backup save name=trunk"
]

# R2 – MikroTik Remoto
cfg_r2 = [
    "/interface bridge add name=br-remote vlan-filtering=yes",
    "/interface bridge port add bridge=br-remote interface=ether2 comment='Hacia R1'",
    "/interface bridge port add bridge=br-remote interface=ether1 comment='Hacia SW2'",
    "/interface bridge vlan add bridge=br-remote vlan-ids=319 untagged=ether1,ether2",
    "/interface bridge vlan add bridge=br-remote vlan-ids=2099 tagged=br-remote,ether1,ether2",
    "/interface vlan add name=gestion2099 vlan-id=2099 interface=br-remote",
    "/ip address add address=10.10.20.4/29 interface=gestion2099",
    "/ip route add dst-address=0.0.0.0/0 gateway=10.10.20.1",
    "/ip service set ssh disabled=no",
    "/ip service set telnet disabled=yes",
    "/ip service set ftp disabled=yes",
    "/ip service set www disabled=yes",
    "/system backup save name=trunk"
]

# === APLICAR CONFIGURACIONES ===
configs = {
    "R1": cfg_r1,
    "SW1": cfg_sw1,
    "SW2": cfg_sw2,
    "R2": cfg_r2
}

for name, dev in devices.items():
    print(f"\n=== Conectando a {name} ({dev['ip']}) ===")
    try:
        conn = ConnectHandler(**dev)
        output = conn.send_config_set(configs[name])
        print(output)
        conn.disconnect()
        print(f"✅ {name} configurado correctamente.\n")
    except Exception as e:
        print(f"❌ Error al configurar {name}: {e}\n")
