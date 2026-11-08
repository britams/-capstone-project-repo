# -*- coding: utf-8 -*-
"""sim_port.py — 시험용 가짜 포트: 관련코딩저장/sim 의 sim_motion.exe / sim_doors.exe --serve 를 띄워
실제 펌웨어 .ino 로직과 표준 입출력으로 이야기한다 (pyserial 대신). 서현 CAP-AI-45
"""
import os
import queue
import subprocess
import threading

SIM_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sim')


class SimPort:
    def __init__(self, exe, *args, speed=5.0, timeout=0.05):
        path = os.path.join(SIM_DIR, exe)
        if not os.path.exists(path):
            raise FileNotFoundError('%s 없음 — 먼저 관련코딩저장/sim/run_all.ps1 로 빌드' % path)
        self.p = subprocess.Popen([path, '--serve', '--speed', str(speed)] + list(args),
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=0)
        self.q = queue.Queue()
        self.timeout = timeout
        threading.Thread(target=self._reader, daemon=True).start()

    def _reader(self):
        for line in iter(self.p.stdout.readline, b''):
            self.q.put(line)

    def readline(self):
        try:
            return self.q.get(timeout=self.timeout)
        except queue.Empty:
            return b''

    def write(self, b):
        self.p.stdin.write(b)
        self.p.stdin.flush()

    def control(self, line):
        """세계 명령 (#BLOCK G2b 1, #RAIL 0 …) — 펌웨어에는 안 감."""
        self.write((line + '\n').encode('ascii'))

    def close(self):
        try:
            self.p.stdin.close()
            self.p.wait(timeout=3)
        except Exception:
            self.p.kill()
