import subprocess
import xml.etree.ElementTree as ET
import json
import sys



def run_nmap(target):
    cmd = ["nmap", "-sV", "-oX",f'nmap_out/xml/{target}.xml', target]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        print("Error: nmap timed out.")
        sys.exit(2)

    if proc.returncode != 0 and not proc.stdout:
        print(f"nmap failed: {proc.stderr.strip()}")
        sys.exit(3)

    return proc.stdout


def parse_nmap_xml(target):
    
    root = ET.parse(f'nmap_out/xml/{target}.xml')
    hosts_data = []

    for host in root.findall("host"):
        addr_el = host.find("address")
        ip = addr_el.get("addr") if addr_el is not None else None

        hostname_el = host.find("hostnames/hostname")
        hostname = hostname_el.get("name") if hostname_el is not None else None

        ports_list = []
        for port_el in host.findall("ports/port"):
            port_id = int(port_el.get("portid"))
            proto = port_el.get("protocol")

            state_el = port_el.find("state")
            state = state_el.get("state") if state_el is not None else None

            service_el = port_el.find("service")
            service_name = service_el.get("name") if service_el is not None else None
            product = service_el.get("product") if service_el is not None else None
            version = service_el.get("version") if service_el is not None else None
            extrainfo = service_el.get("extrainfo") if service_el is not None else None

            ports_list.append({
                "port": port_id,
                "proto": proto,
                "state": state,
                "service": service_name,
                "product": product,
                "version": version,
                "extrainfo": extrainfo
            })

        hosts_data.append({
            "hostname": hostname,
            "ip": ip,
            "ports": ports_list
        })

    return hosts_data



if __name__ == "__main__":
    target = input('Target : ')
    nmaprun = run_nmap(target)
    print(nmaprun)
    parsed_data = parse_nmap_xml(target)

    out_file = f"nmap_out/{target}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(parsed_data, f, indent=4)

    print(f"Probed {target} host saved to {out_file}")
