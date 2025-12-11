from tango.server import run

from buk_m.power_supply import power_supply
from buk_m.buk_m1 import BUK_M1

if __name__ == "__main__":
    run([power_supply])
