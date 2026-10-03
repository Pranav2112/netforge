# Networking design

> Planned design for v1. Sections are filled in as each phase is implemented
> and verified.

## Topology v1

Four routers in a square plus the R2–R3 diagonal, one host LAN per router.

| Link | Subnet | Lower router | Higher router |
|---|---|---|---|
| R1–R2 | 10.0.12.0/31 | R1 .0 | R2 .1 |
| R1–R3 | 10.0.13.0/31 | R1 .0 | R3 .1 |
| R2–R3 | 10.0.23.0/31 | R2 .0 | R3 .1 |
| R2–R4 | 10.0.24.0/31 | R2 .0 | R4 .1 |
| R3–R4 | 10.0.34.0/31 | R3 .0 | R4 .1 |

| Node | ASN | Loopback / router-id | LAN | Host |
|---|---|---|---|---|
| R1 | 65001 | 10.255.0.1/32 | 10.1.0.0/24 (gw .1) | H1 10.1.0.10 |
| R2 | 65002 | 10.255.0.2/32 | 10.2.0.0/24 (gw .1) | H2 10.2.0.10 |
| R3 | 65003 | 10.255.0.3/32 | 10.3.0.0/24 (gw .1) | H3 10.3.0.10 |
| R4 | 65004 | 10.255.0.4/32 | 10.4.0.0/24 (gw .1) | H4 10.4.0.10 |

### Rationale

- **/31 point-to-point links (RFC 3021):** a two-node link needs no network or
  broadcast address.
- **One ASN per router (RFC 7938 style):** every session is eBGP between
  directly connected peers, so no IGP is needed for next-hop reachability.
  An IGP becomes necessary once an AS has several routers (Phase 11).
- **Equal-length paths (R1→R4 via R2 or R3):** make BGP tie-breaking, ECMP, and
  AS-path prepending observable.
- **Address ranges** avoid Docker (172.17.0.0/16+), the containerlab management
  network (172.20.20.0/24), and Colima/Lima (192.168.5.0/24).
- **Management network:** each node's `eth0` is out-of-band management only.
  Hosts route 10.0.0.0/8 via their router, and FRR never advertises the
  management prefix, so lab traffic cannot bypass the routed network.

## Sections to come

- Phase 1: namespaces, veth, bridges
- Phase 2: ARP, forwarding, static routing
- Phase 3: FRR architecture, RIB vs FIB
- Phase 4: BGP sessions, policy, best-path selection
