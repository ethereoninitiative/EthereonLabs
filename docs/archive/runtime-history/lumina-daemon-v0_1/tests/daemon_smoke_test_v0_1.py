import subprocess
import sys

CMD = [sys.executable, "../lumina_daemon_v0_1.py"]


def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def test_sequence():
    rc, out, err = run(CMD + ["start"])
    assert rc == 0

    rc, out, err = run(CMD + ["checkpoint", "--label", "test"])
    assert rc == 0

    rc, out, err = run(CMD + ["stop"])
    assert rc == 0

    rc, out, err = run(CMD + ["start"])
    assert rc == 0

    rc, out, err = run(CMD + ["status"])
    assert rc == 0

    print("Daemon smoke test passed")


if __name__ == "__main__":
    test_sequence()
