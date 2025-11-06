---

# 🔧 Proyecto de Red – MikroTik + VLAN + Portal Cautivo

## 📘 Descripción General

Este proyecto implementa una **infraestructura de red segmentada mediante VLANs** sobre **MikroTik RouterOS 7**, diseñada para ofrecer seguridad, control y administración centralizada.
Se configuró un **portal cautivo (Hotspot)**, múltiples redes VLAN para distintos departamentos, un **servidor DHCP por VLAN**, y una **interfaz de gestión** para el administrador del sistema.

El objetivo es crear una topología escalable, segura y fácilmente mantenible, donde cada red se mantenga aislada pero administrable desde la red de gestión.

---

## 🧩 Topología Lógica

```
                  ┌──────────────────────┐
                  │      MikroTik R1     │
                  │----------------------│
                  │  VLAN 10 - Admin     │
                  │  VLAN 20 - Ventas    │
                  │  VLAN 30 - Clientes  │
                  │  VLAN 2099 - Gestión │
                  └─────────┬────────────┘
                            │
                            │ Trunk (ens3)
                            │
            ┌─────────────────────────────────┐
            │          Switch VLAN            │
            └─────────────────────────────────┘
                            │
               ┌────────────┴────────────┐
               │                         │
       Sysadmin PC (Gestión)      Clientes / Equipos
```

---

## 🧱 VLANs Configuradas

| VLAN ID |   Descripción   |  Rango de IPs | Gateway    | Interfaz | DHCP | Comentarios                            |
| :-----: | :-------------: | :-----------: | :--------- | :------- | :--: | :------------------------------------- |
|    10   |  Administración | 10.10.10.0/29 | 10.10.10.1 | ether2   |   ✅  | Red interna de administración          |
|    20   |      Ventas     | 10.10.11.0/29 | 10.10.11.1 | ether3   |   ✅  | Equipos del área comercial             |
|    30   | Clientes / WiFi | 10.10.12.0/29 | 10.10.12.1 | ether4   |   ✅  | Hotspot y acceso público               |
|   2099  |     Gestión     | 10.10.20.0/29 | 10.10.20.1 | ether5   |   ✅  | VLAN de administración de dispositivos |

---

## ⚙️ Configuración DHCP por VLAN

Cada VLAN cuenta con un servidor DHCP independiente para asignar direcciones dentro de su rango.

### 🟢 Ejemplo: VLAN de Gestión (2099)

```bash
/ip pool
add name=pool-gestion ranges=10.10.20.2-10.10.20.6

/ip dhcp-server
add name=dhcp-gestion interface=VLAN2099 address-pool=pool-gestion lease-time=10m disabled=no

/ip dhcp-server network
add address=10.10.20.0/29 gateway=10.10.20.1 dns-server=1.1.1.1,8.8.8.8
```

---

## 🌐 Rutas y Acceso a Internet

Se configuró una **ruta por defecto** hacia el ISP para todas las VLANs:

```bash
/ip route
add dst-address=0.0.0.0/0 gateway=ISP-GW
```

Cada VLAN puede acceder a Internet a través del gateway MikroTik (con **masquerade** activado en NAT):

```bash
/ip firewall nat
add chain=srcnat action=masquerade out-interface=ether1 comment="NAT para VLANs"
```

---


---

## 🖥️ Configuración del Cliente Sysadmin (Linux)

En el equipo de administración se configuró una IP estática dentro de la VLAN de gestión (2099):

```bash
sudo ip addr flush dev ens3
sudo ip addr add 10.10.20.5/29 dev ens3
sudo ip link set ens3 up
sudo ip route add default via 10.10.20.1
```

Esto permite la gestión remota del MikroTik y de los equipos conectados a la VLAN de administración.

---

## 🧠 Notas Técnicas

* **Sistema base:** MikroTik RouterOS v7.x
* **Cliente:** Linux Alpine
* **Interconexión:** Trunk 802.1Q
* **Segmentación:** Basada en VLANs por área funcional
* **Gestión centralizada:** VLAN 2099
* **DNS externos:** 1.1.1.1 y 8.8.8.8

---

## 🏁 Conclusión

El proyecto consolida una arquitectura de red modular y segura:

* Cada departamento opera en su propia VLAN aislada.
* El administrador puede gestionar toda la infraestructura desde una única red de gestión.
* Los clientes acceden mediante un portal cautivo controlado.
* Toda la comunicación inter-VLAN pasa por el MikroTik, asegurando control total del tráfico.

---

