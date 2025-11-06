from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException

# Datos de conexión comunes
devices = {
    "SW1": {
        "device_type": "cisco_ios",
        "host": "10.10.20.2",
        "username": "admin",
        "password": "1234",
    },
    "SW2": {
        "device_type": "cisco_ios",
        "host": "10.10.20.3",
        "username": "admin",
        "password": "1234",
    },
    "R1": {
        "device_type": "mikrotik_routeros",
        "host": "10.10.20.1",
        "username": "admin",
        "password": "1234",
    },
    "R2": {
        "device_type": "mikrotik_routeros",
        "host": "10.10.20.4",
        "username": "admin",
        "password": "1234",
    }
}

# Configuración de SW1
cfg_sw1 = [
    "vlan 310", "name VENTAS",
    "vlan 311", "name TECNICA",
    "vlan 312", "name VISITANTES",
    # VLANs ya creadas: 2099 (gestion), 319 (nativa trunk)
    # Puertos access
    "interface Ethernet0/1",
    " switchport mode access",
    " switchport access vlan 310",
    " no shutdown",
    "exit",
    "interface Ethernet0/2",
    " switchport mode access",
    " switchport access vlan 311",
    " no shutdown",
    "exit",
    "interface Ethernet0/3",
    " switchport mode access",
    " switchport access vlan 312",
    " no shutdown",
    "exit",
    # Trunk hacia R1
    "interface Ethernet0/0",
    " switchport trunk encapsulation dot1q",
    " switchport mode trunk",
    " switchport trunk native vlan 319",
    " switchport trunk allowed vlan 319,310,311,312,2099",
    " no shutdown",
    "exit",
]

# Configuración de SW2 (trunk + puerto usuario remoto en gestión)
cfg_sw2 = [
    "vlan 310", "name VENTAS",
    "vlan 311", "name TECNICA",
    "vlan 312", "name VISITANTES",
    "interface Ethernet0/1",
    " switchport mode access",
    " switchport access vlan 2099",   # PC remota ahora en VLAN Gestión
    " no shutdown",
    "exit",
    "interface Ethernet0/0",
    " switchport trunk encapsulation dot1q",
    " switchport mode trunk",
    " switchport trunk native vlan 319",
    " switchport trunk allowed vlan 319,310,311,312,2099",
    " no shutdown",
    "exit",
]

# Configuración de R1 (Router-on-a-Stick + NAT + DHCP)
# VLAN de gestión 2099 ya configurada con IP 10.10.20.1/29
cfg_r1 = [
    # Subinterfaces para VLANs de usuario
    "/interface vlan add name=VLAN310 vlan-id=310 interface=ether2",
    "/interface vlan add name=VLAN311 vlan-id=311 interface=ether2",
    "/interface vlan add name=VLAN312 vlan-id=312 interface=ether2",

    # Direccionamiento para las VLANs de usuario (VLSM aplicado)
    "/ip address add address=10.10.20.33/27 interface=VLAN310",  # Ventas
    "/ip address add address=10.10.20.65/28 interface=VLAN311",  # Técnica
    "/ip address add address=10.10.20.81/29 interface=VLAN312",  # Visitantes

    # NAT solo para Ventas y Técnica
    "/ip firewall nat add chain=srcnat src-address=10.10.20.32/27 action=masquerade out-interface=ether1",
    "/ip firewall nat add chain=srcnat src-address=10.10.20.64/28 action=masquerade out-interface=ether1",

    # DHCP para Ventas y Técnica
    "/ip pool add name=POOL_VLAN310 ranges=10.10.20.34-10.10.20.62",
    "/ip dhcp-server add name=DHCP310 interface=VLAN310 lease-time=1h address-pool=POOL_VLAN310",
    "/ip dhcp-server network add address=10.10.20.32/27 gateway=10.10.20.33 dns-server=8.8.8.8",

    "/ip pool add name=POOL_VLAN311 ranges=10.10.20.66-10.10.20.78",
    "/ip dhcp-server add name=DHCP311 interface=VLAN311 lease-time=1h address-pool=POOL_VLAN311",
    "/ip dhcp-server network add address=10.10.20.64/28 gateway=10.10.20.65 dns-server=8.8.8.8",
]

# Configuración de R2 (remoto, puente transparente para todas las VLANs)
cfg_r2 = [
    # VLANs en el bridge remoto
    "/interface bridge vlan add bridge=br-remote vlan-ids=319 untagged=ether1,ether2",
    "/interface bridge vlan add bridge=br-remote vlan-ids=2099 tagged=br-remote,ether1,ether2",
    "/interface bridge vlan add bridge=br-remote vlan-ids=310 tagged=ether1,ether2",
    "/interface bridge vlan add bridge=br-remote vlan-ids=311 tagged=ether1,ether2",
    "/interface bridge vlan add bridge=br-remote vlan-ids=312 tagged=ether1,ether2",
]

# Comandos de verificación
verify_cmds = {
    "SW1": ["show vlan brief", "show ip interface brief"],
    "SW2": ["show vlan brief", "show ip interface brief"],
    "R1": ["/ip address print", "/ip route print", "/ip dhcp-server print", "/interface vlan print"],
    "R2": ["/ip address print", "/ip route print", "/interface vlan print"],
}

# Ejecución
for name, device in devices.items():
    print(f"\n###### Conectando a {name} ({device['host']}) ######")
    try:
        with ConnectHandler(**device) as conn:
            if name == "SW1":
                print(f"--- Aplicando configuración a {name} ---")
                output = conn.send_config_set(cfg_sw1)
                print(output)
            elif name == "SW2":
                print(f"--- Aplicando configuración a {name} ---")
                output = conn.send_config_set(cfg_sw2)
                print(output)
            elif name == "R1":
                print(f"--- Aplicando configuración a {name} ---")
                for cmd in cfg_r1:
                    print(f"Ejecutando: {cmd}")
                    output = conn.send_command(cmd)
                    if output:
                        print(f"Output: {output}")
            elif name == "R2":
                print(f"--- Aplicando configuración a {name} ---")
                for cmd in cfg_r2:
                    print(f"Ejecutando: {cmd}")
                    output = conn.send_command(cmd)
                    if output:
                        print(f"Output: {output}")

            print(f"\n-- Verificación en {name} --")
            for vcmd in verify_cmds[name]:
                print(f"\n{name}# {vcmd}")
                output = conn.send_command(vcmd)
                print(f"{output}\n")

    except NetmikoTimeoutException:
        print(f"ERROR: Timeout al conectar con {name} ({device['host']}). Verifique la conectividad y las credenciales.")
    except NetmikoAuthenticationException:
        print(f"ERROR: Autenticación fallida para {name} ({device['host']}). Verifique el usuario y la contraseña.")
    except Exception as e:
        print(f"ERROR: Ocurrió un error inesperado al conectar o configurar {name}: {e}")

print("\n##### Proceso de configuración completado #####")
