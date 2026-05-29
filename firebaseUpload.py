import random

# ================= DEVICE STATES =================

device_states = {

    "lamp1": 0,
    "lamp2": 0,
    "fan": 0,
    "ac": 0,
    "tv": 0,
    "security": 0

}

# ================= DEVICE POWER USAGE =================

device_power = {

    "lamp1": 40,
    "lamp2": 40,
    "fan": 120,
    "ac": 1200,
    "tv": 180,
    "security": 60

}

# ================= CONTROL DEVICE =================

def writeFirebase(appliance, action):

    device_states[appliance] = int(action)

    print(f"{appliance} set to {action}")

# ================= READ SMART DATA =================

def readFirebase():

    # Base voltage
    voltage = random.randint(220, 240)

    # Base current
    current = 0.3

    # Calculate total power
    total_power = 0

    for device, status in device_states.items():

        if status == 1:

            total_power += device_power[device]

    # Small random fluctuation
    total_power += random.randint(1, 5)

    # Calculate current using formula:
    # Current = Power / Voltage

    current += round(total_power / voltage, 2)

    return voltage, round(current, 2), total_power