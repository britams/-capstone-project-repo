# -*- coding: utf-8 -*-
"""ports.py — 두 UNO 를 READY 이름으로 가려낸다 (검토 문서 CAP-AI-42 ‘Pi 포트는 READY 이름으로 구분’)

/dev/ttyACM0 · ACM1 순서는 켤 때마다 바뀔 수 있다 [가능성 높음] → 포트 이름을 믿지 않고
각 포트가 'EVT READY trap_motion …' / 'EVT READY trap_doors …' 중 무엇을 말하는지로 정한다.
"""
from uno_link import UnoLink, LinkError


def identify(ports, ready_timeout=6.0, clock=None):
    """ports: port 객체(또는 (label, port)) 목록. 돌려주는 값: {'trap_motion': UnoLink, 'trap_doors': UnoLink}"""
    links = []
    for i, p in enumerate(ports):
        label, port = p if isinstance(p, tuple) else ('port%d' % i, p)
        links.append(UnoLink(port, label=label, **({'clock': clock} if clock else {})))
    found = {}
    for lk in links:
        if not lk.wait_ready(ready_timeout):
            try:
                lk.identify_by_status()          # READY 를 놓친 경우
            except LinkError:
                pass
        if lk.name is None:
            raise LinkError('%s: READY 도 STATUS 도 못 알아봄 (UNO 아님? 펌웨어 안 올라감?)' % lk.label)
        if lk.name in found:
            raise LinkError('같은 이름 %s 가 두 포트(%s, %s)에서 옴' % (lk.name, found[lk.name].label, lk.label))
        found[lk.name] = lk
    for need in ('trap_motion', 'trap_doors'):
        if need not in found:
            raise LinkError('%s 포트를 못 찾음 (찾은 것: %s)' % (need, ', '.join(sorted(found)) or '없음'))
    return found


def open_serial_ports(names=None, baud=115200):
    """pyserial 로 실제 포트를 연다. names 없으면 Arduino 로 보이는 USB 시리얼을 모두.
    (Pi: pip install pyserial.  UNO 는 열면 재부팅하므로 identify() 가 READY 를 기다린다.)"""
    import serial                                    # pyserial — 시험(SimPort)에서는 필요 없음
    from serial.tools import list_ports
    if names is None:
        names = [p.device for p in list_ports.comports()
                 if (p.vid in (0x2341, 0x2A03, 0x1A86, 0x0403)) or 'ACM' in p.device or 'Arduino' in (p.manufacturer or '')]
    return [(n, serial.Serial(n, baud, timeout=0.05)) for n in sorted(names)]
