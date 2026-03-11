# Open5GS Roaming Setup

## Modified Source Files

**`lib/sbi/message.c`**

**`src/amf/`**
- `amf-sm.c`
- `namf-handler.h`
- `namf-handler.c`

**`src/smf/`**
- `smf-sm.c`
- `nsmf-handler.h`
- `nsmf-handler.c`

---

## Build & Install

After modifying the source code, rebuild and install with:
```bash
meson compile -C build
meson install -C build
```

---

## Configuration

The YAML config files are located at `install/etc/open5gs/`.

> ⚠️ **Note:** Update file paths to match local environment.  
> For example, in `amf.yaml`, update the logger path:
```yaml
logger:
  file:
    path: /home/<your-username>/open5gs/install/var/log/open5gs/amf.log
#  level: info   # fatal|error|warn|info(default)|debug|trace
```

All other configuration values remain unchanged.

---

## Starting the Core Networks

### Home Network
```bash
sudo ./install/bin/open5gs-nrfd -c ./install/etc/open5gs/h-nrf.yaml
./install/bin/open5gs-scpd -c ./install/etc/open5gs/h-scp.yaml
sudo ./install/bin/open5gs-ausfd
sudo ./install/bin/open5gs-udmd
./install/bin/open5gs-udrd
./install/bin/open5gs-amfd -c ./install/etc/open5gs/h-amf.yaml
sudo ./install/bin/open5gs-smfd -c ./install/etc/open5gs/h-smf.yaml
sudo ./install/bin/open5gs-upfd -c ./install/etc/open5gs/h-upf.yaml
./install/bin/open5gs-pcfd -c ./install/etc/open5gs/h-pcf.yaml
./install/bin/open5gs-bsfd -c ./install/etc/open5gs/h-bsf.yaml
sudo ./install/bin/open5gs-nssfd -c ./install/etc/open5gs/h-nssf.yaml
./install/bin/open5gs-seppd -c ./install/etc/open5gs/sepp1.yaml
```

### Visited Network
```bash
sudo ./install/bin/open5gs-nrfd
./install/bin/open5gs-scpd
./install/bin/open5gs-amfd
sudo ./install/bin/open5gs-smfd
./install/bin/open5gs-upfd
./install/bin/open5gs-pcfd
./install/bin/open5gs-bsfd
sudo ./install/bin/open5gs-nssfd
./install/bin/open5gs-seppd -c ./install/etc/open5gs/sepp2.yaml
```

---

## PacketRusher Config Files

> These are the config files used in this project. The full PacketRusher repository contains additional files.

`roaming-vplmn-001-hplmn-999.yaml`： Roaming config,supports both 
`hplmn-999.yaml`: Config for connecting to the Home Network only

---

## Testing

`test.py` can be run to reproduce the AMF and SMF logs demonstrated in the meeting on 2026-03-11.
