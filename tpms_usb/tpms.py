"""USB TPMS dongle (CH340 1a86:7523, 19200 8N1) -> JSON lines on stdout.

Frame: 55 AA 08 pos press temp status xor   (xor of the first 7 bytes)
  press * 3.44 kPa, temp - 50 degC. pos: 00/01 front L/R, 10/11 rear L/R, 05 = spare slot.
"""
import glob, json, os, sys, termios, time

POS = {0x00: "front_left", 0x01: "front_right", 0x10: "rear_left", 0x11: "rear_right", 0x05: "spare"}
REPUBLISH_S = 60  # dongle repeats cached values forever; this only keeps expire_after alive


def decode(frame):
    x = 0
    for b in frame[:7]:
        x ^= b
    if frame[:3] != b"\x55\xaa\x08" or x != frame[7]:
        return None
    return POS.get(frame[3], "pos_%02x" % frame[3]), {
        "bar": round(frame[4] * 3.44 / 100, 2), "temp": frame[5] - 50, "status": frame[6]}


def split(buf):
    """Return (decoded frames, leftover bytes)."""
    out = []
    while True:
        i = buf.find(b"\x55\xaa")
        if i < 0:
            return out, buf[-1:]
        if len(buf) - i < 8:
            return out, buf[i:]
        d = decode(buf[i:i + 8])
        if d:
            out.append(d)
            buf = buf[i + 8:]
        else:
            buf = buf[i + 1:]


def find_port():
    for tty in glob.glob("/sys/class/tty/ttyUSB*"):
        usb = os.path.realpath(tty + "/device") + "/../.."
        try:
            if open(usb + "/idVendor").read().strip() == "1a86" and open(usb + "/idProduct").read().strip() == "7523":
                return "/dev/" + os.path.basename(tty)
        except OSError:
            pass
    sys.exit("TPMS dongle (1a86:7523) not found")


def open_port(path):
    fd = os.open(path, os.O_RDONLY | os.O_NOCTTY)
    a = termios.tcgetattr(fd)
    a[0] = a[1] = a[3] = 0
    a[2] = termios.CS8 | termios.CREAD | termios.CLOCAL
    a[4] = a[5] = termios.B19200
    a[6][termios.VMIN], a[6][termios.VTIME] = 1, 0
    termios.tcsetattr(fd, termios.TCSANOW, a)
    return fd


def main():
    fd = open_port(find_port())
    state, buf, last = {}, b"", 0
    while True:
        chunk = os.read(fd, 64)
        if not chunk:
            sys.exit("dongle unplugged")
        frames, buf = split(buf + chunk)
        changed = False
        for pos, v in frames:
            changed |= state.get(pos) != v
            state[pos] = v
        if state and (changed or time.time() - last > REPUBLISH_S):
            print(json.dumps(state, sort_keys=True))
            last = time.time()


def demo():
    raw = bytes.fromhex("aa0855aa080098440 02b55aa08019b45002855aa0805495300e855aa0800".replace(" ", ""))
    frames, rest = split(raw)
    assert frames[0] == ("front_left", {"bar": 5.23, "temp": 18, "status": 0}), frames
    assert [p for p, _ in frames] == ["front_left", "front_right", "spare"], frames
    assert rest == b"\x55\xaa\x08\x00"
    assert decode(bytes.fromhex("55aa0800984400ff")) is None
    print("ok")


if __name__ == "__main__":
    demo() if sys.argv[1:] == ["demo"] else main()
