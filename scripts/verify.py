#!/usr/bin/env python3
"""Static invariants only; this is not the Shadowrocket parser or an iOS test."""
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
text = (ROOT / 'claude-guard.conf').read_text()
assert text == (ROOT / 'claude-guard-2.2.92.conf').read_text(), 'download variants diverged'
sections = {}
section = None
for raw in text.splitlines():
    line = raw.strip()
    if not line or line.startswith('#'):
        continue
    if line.startswith('['):
        assert line.endswith(']') and line not in sections, 'invalid/duplicate section'
        section = line
        sections[section] = []
    else:
        assert section, 'value outside section'
        sections[section].append(line)

def settings(name):
    pairs = [line.split('=', 1) for line in sections[name]]
    result = {k.strip(): v.strip() for k, v in pairs}
    assert len(pairs) == len(result), f'duplicate key in {name}'
    return result

general = settings('[General]')
for key in ('dns-server', 'fallback-dns-server'):
    values = general[key].split(',')
    assert values and all(v.startswith('https://') and v.endswith('#proxy') for v in values), key
assert general['proxy-dns-server'] == 'https://223.5.5.5/dns-query'
assert general['dns-direct-system'] == 'false'
assert general['udp-policy-not-supported-behaviour'] == 'REJECT'
assert not any('server:system' in s for s in sections['[Host]'])
assert settings('[MITM]')['enable'] == 'false'
assert not sections['[Proxy]'], 'public config must not include private nodes'

groups = settings('[Proxy Group]')
assert groups['AI'] == 'select,PROXY,policy-select-name=PROXY'
known = set(groups) | {'DIRECT', 'PROXY', 'REJECT'}
for name, value in groups.items():
    for option in value.split(',')[1:]:
        if '=' not in option:
            assert option in known, f'{name}: undefined group option {option}'

rules = sections['[Rule]']
expected = [s for s in (ROOT / 'claude.list').read_text().splitlines() if s and not s.startswith('#')]
assert len(expected) == 16 and len(set(expected)) == 16
assert rules[:16] == [s + ',AI' for s in expected], 'priority rules changed'
assert rules[-1] == 'FINAL,PROXY'
assert sum(r.startswith('FINAL,') for r in rules) == 1
remote = []
for rule in rules:
    parts = rule.split(',')
    assert parts[-1] in known, f'undefined policy: {rule}'
    if parts[0] == 'RULE-SET':
        url = urlparse(parts[1])
        assert url.scheme == 'https' and url.hostname == 'raw.githubusercontent.com'
        assert '/QuantumultX/' not in url.path, 'wrong rule-set dialect'
        remote.append(parts[1])
for service in ('Google', 'Twitter', 'YouTube', 'Telegram'):
    assert any('/' + service + '/' in u for u in remote), f'missing community rule set: {service}'
print(f'PASS: 16 priority rules; {len(rules)} total rules; {len(remote)} remote sets; {len(groups)} groups')
print('PASS: proxied DNS including fallback; no system host override; no private nodes; MITM disabled')
print('Not covered: native parser, phone import, remote rule-set contents, real DNS/IPv6/WebRTC/failure behavior')
