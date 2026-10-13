"""Verify the credential-free mobile routing mirror."""
import ipaddress
import json
import runpy
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
b = runpy.run_path(str(ROOT / 'scripts/verify.py'))
text = (ROOT / 'desktop-public.conf').read_text(encoding='utf-8')
m = json.loads((ROOT / 'public-mirror-manifest.json').read_text(encoding='utf-8'))
assert not text.split('[Proxy]\n', 1)[1].split('[Proxy Group]', 1)[0].strip()
assert 'RULE-SET,' not in text and 'raw.githubusercontent.com' not in text
assert 'password=' not in text.lower() and 'username=' not in text.lower()
group = next(l for l in text.splitlines() if l.startswith(m['transitGroup'] + ' = ')).split(' = ', 1)[1].split(',')
assert group[0] == 'select' and group[1:-1] == m['transitMembers']
assert group[-1] == 'policy-select-name=' + m['sourceTransit']
split = b['split_rule']
rows = [split(s) for s in text.split('[Rule]\n', 1)[1].split('[Host]', 1)[0].splitlines() if s.strip()]
assert len(rows) == m['inlineRuleCount']
def compile_rule(p):
    k = p[0]
    if k == 'FINAL': return k, None
    if k in ('IP-CIDR', 'IP-CIDR6'): return 'IP', ipaddress.ip_network(p[1])
    if k == 'AND': return k, [compile_rule(split(t[1:-1])) for t in split(p[1][1:-1])]
    assert k in ('DOMAIN', 'DOMAIN-SUFFIX', 'DOMAIN-KEYWORD', 'PROTOCOL')
    return k, p[1]
compiled = [(compile_rule(p), p[-2] if p[-1] == 'no-resolve' else p[-1]) for p in rows]
def match(c, h, a, proto):
    k, v = c
    if k == 'FINAL': return True
    if k == 'DOMAIN': return h == v
    if k == 'DOMAIN-SUFFIX': return h == v or h.endswith('.' + v)
    if k == 'DOMAIN-KEYWORD': return v in h
    if k == 'PROTOCOL': return proto == v
    if k == 'IP': return a.version == v.version and a in v
    if k == 'AND': return all(match(x, h, a, proto) for x in v)
for h, ip, proto, expected in b['cases']:
    a = ipaddress.ip_address(ip)
    actual = next(policy for c, policy in compiled if match(c, h, a, proto))
    assert actual == m['policyMap'][expected], (h, proto)
print(f'PASS: public mirror, {len(group)-2} selectable transit names, {len(rows)} inline rules, 26 routing cases, no node definitions')
print('Not verified: native iOS parser and on-device proxy-chain behavior')
