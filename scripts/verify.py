#!/usr/bin/env python3
"""Offline routing checks, not the native Shadowrocket parser or an iOS test."""
import hashlib
import ipaddress
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
text = (ROOT / 'claude-guard.conf').read_text(encoding='utf-8')
assert text == (ROOT / 'claude-guard-2.2.92.conf').read_text(encoding='utf-8'), 'variants diverged'
assert (ROOT / 'VERSION').read_text().strip() in text
sections, current = {}, None
for raw in text.splitlines():
    line = raw.strip()
    if not line or line.startswith('#'): continue
    if line.startswith('['):
        assert line.endswith(']') and line not in sections
        current = line
        sections[current] = []
    else:
        assert current
        sections[current].append(line)

def settings(section):
    pairs = [v.split('=', 1) for v in sections[section]]
    result = {k.strip(): v.strip() for k, v in pairs}
    assert len(result) == len(pairs)
    return result

g = settings('[General]')
for key in ('dns-server', 'fallback-dns-server'):
    assert all(v.startswith('https://') and v.endswith('#proxy') for v in g[key].split(','))
assert g['direct-dns-server'] == '119.29.29.29,223.5.5.5,system'
assert g['proxy-dns-server'] == 'https://223.6.6.6/dns-query,https://120.53.53.53/dns-query'
assert g['udp-policy-not-supported-behaviour'] == 'REJECT'
assert g['close-if-proxy-chain-missing'] == 'true'
assert g['tun-excluded-routes'] == ''
assert g['skip-proxy'] == 'localhost,*.local'
assert g['dns-direct-system'] == 'false'
assert settings('[MITM]')['enable'] == 'false'
assert not sections['[Proxy]']
assert not sections['[URL Rewrite]']
groups = settings('[Proxy Group]')
assert groups == {
    '海外TCP': 'select,PROXY,policy-select-name=PROXY',
    '国内及局域网': 'select,DIRECT,policy-select-name=DIRECT',
    '苹果服务': 'select,DIRECT,policy-select-name=DIRECT',
    '微软服务': 'select,DIRECT,policy-select-name=DIRECT',
    '海外UDP': 'select,REJECT,policy-select-name=REJECT',
}
manifest = json.loads((ROOT / 'rules/manifest.json').read_text(encoding='utf-8'))
datasets = {}
for name, meta in manifest['files'].items():
    data = (ROOT / 'rules' / name).read_bytes()
    assert hashlib.sha256(data).hexdigest() == meta['sha256'], name
    rows = [r for r in data.decode().splitlines() if r and not r.startswith('#')]
    assert len(rows) == len(set(rows)) == meta['rules'], name
    exact, suffixes, keywords, networks = set(), set(), [], []
    for row in rows:
        kind, value = row.split(',', 1)
        assert ',' not in value
        if kind == 'DOMAIN': exact.add(value)
        elif kind == 'DOMAIN-SUFFIX': suffixes.add(value)
        elif kind == 'DOMAIN-KEYWORD': keywords.append(value)
        elif kind in ('IP-CIDR', 'IP-CIDR6'): networks.append(ipaddress.ip_network(value))
        else: raise AssertionError(kind)
    datasets[name] = (exact, suffixes, keywords, networks)
assert len(manifest['omitted']) == 1 and manifest['omitted'][0]['dataset'] == 'private'

def split_rule(line):
    parts, depth, start = [], 0, 0
    for i, ch in enumerate(line):
        depth += (ch == '(') - (ch == ')')
        assert depth >= 0
        if ch == ',' and depth == 0:
            parts.append(line[start:i]); start = i + 1
    assert depth == 0
    return parts + [line[start:]]

rules = sections['[Rule]']
remote = []
for line in rules:
    p = split_rule(line)
    policy = p[-2] if p[-1] == 'no-resolve' else p[-1]
    assert policy in groups, line
    assert p[0] != 'PROTOCOL'
    if p[0] == 'RULE-SET':
        u = urlparse(p[1])
        assert u.scheme == 'https' and u.hostname == 'raw.githubusercontent.com'
        assert u.path.startswith('/gozelus/shadowrocket-rules/main/rules/')
        remote.append(Path(u.path).name)
assert remote == ['private-domains.list','github-copilot-proxy.list','apple-domains.list','microsoft-domains.list','cn-domains.list','cn-ip.list']
assert rules.index('RULE-SET,https://raw.githubusercontent.com/gozelus/shadowrocket-rules/main/rules/github-copilot-proxy.list,海外TCP') < rules.index('RULE-SET,https://raw.githubusercontent.com/gozelus/shadowrocket-rules/main/rules/microsoft-domains.list,微软服务')
assert rules[-3:] == [
    'AND,((PROTOCOL,UDP),(IP-CIDR,0.0.0.0/0)),海外UDP',
    'AND,((PROTOCOL,UDP),(IP-CIDR6,::/0)),海外UDP', 'FINAL,海外TCP']
assert sum(r.startswith('FINAL,') for r in rules) == 1

def matches(name, host, address):
    exact, suffixes, keywords, networks = datasets[name]
    parts = host.lower().split('.')
    return (host.lower() in exact
            or any('.'.join(parts[i:]) in suffixes for i in range(len(parts)))
            or any(k in host.lower() for k in keywords)
            or any(address.version == n.version and address in n for n in networks))

def route(host, ip, protocol):
    address = ipaddress.ip_address(ip)
    def condition(p):
        if p[0] == 'RULE-SET': return matches(Path(urlparse(p[1]).path).name, host, address)
        if p[0] == 'PROTOCOL': return protocol == p[1]
        if p[0] in ('IP-CIDR', 'IP-CIDR6'):
            n = ipaddress.ip_network(p[1])
            return address.version == n.version and address in n
        if p[0] == 'AND':
            terms = split_rule(p[1][1:-1])
            return all(condition(split_rule(term[1:-1])) for term in terms)
        raise AssertionError('unsupported condition ' + p[0])
    for line in rules:
        p = split_rule(line)
        if p[0] == 'FINAL': return p[1]
        if condition(p): return p[2]
    raise AssertionError('unmatched')

cases = [
 ('www.baidu.com','1.1.1.1','TCP','国内及局域网'),
 ('www.qq.com','1.1.1.1','UDP','国内及局域网'),
 ('router.asus.com','1.1.1.1','TCP','国内及局域网'),
 ('','192.168.1.20','UDP','国内及局域网'),
 ('','fe80::1','UDP','国内及局域网'),
 ('','::1','TCP','国内及局域网'),
 ('unknown.example.org','223.5.5.5','UDP','国内及局域网'),
 ('www.apple.com','1.1.1.1','TCP','苹果服务'),
 ('www.icloud.com','1.1.1.1','UDP','苹果服务'),
 ('www.microsoft.com','1.1.1.1','TCP','微软服务'),
 ('login.microsoftonline.com','1.1.1.1','UDP','微软服务'),
 ('github.com','1.1.1.1','TCP','海外TCP'),
 ('raw.githubusercontent.com','1.1.1.1','TCP','海外TCP'),
 ('api.individual.githubcopilot.com','1.1.1.1','TCP','海外TCP'),
 ('github.com','1.1.1.1','UDP','海外UDP'),
 ('copilot.microsoft.com','1.1.1.1','TCP','海外TCP'),
 ('copilot.cloud.microsoft','1.1.1.1','UDP','海外UDP'),
 ('default.exp-tas.com','1.1.1.1','TCP','海外TCP'),
 ('claude.ai','1.1.1.1','TCP','海外TCP'),
 ('api.anthropic.com','1.1.1.1','TCP','海外TCP'),
 ('www.google.com','1.1.1.1','TCP','海外TCP'),
 ('new-telemetry.example.org','1.1.1.1','TCP','海外TCP'),
 ('browser-intake-us5-datadoghq.com','1.1.1.1','TCP','海外TCP'),
 ('stun.l.google.com','1.1.1.1','UDP','海外UDP'),
 ('ipv6.example.org','2606:4700:4700::1111','UDP','海外UDP'),
 ('ipv6.example.org','2606:4700:4700::1111','TCP','海外TCP'),
]
for host, ip, proto, expected in cases:
    assert route(host, ip, proto) == expected, (host, ip, proto, expected)
assert not re.search(r'(?i)(password|username)\s*=', text)
print(f'PASS: {len(rules)} rules, {len(groups)} groups, {len(cases)} routing cases, {len(datasets)} dataset hashes')
print('PASS: Apple/Microsoft direct; public DNS proxied; no private nodes; MITM disabled')
print('Not covered: native parser, iOS import, actual DNS/IPv6/WebRTC/disconnection behavior')
