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

    total_power = 0

    for device, status in device_states.items():

        if status == 1:

            total_power += device_power[device]

    # Voltage

    if total_power > 0:

        voltage = random.randint(228, 235)

    else:

        voltage = 230

    # Current

    if total_power > 0:

        current = round(
            total_power / voltage,
            2
        )

    else:

        current = 0

    return (
        voltage,
        current,
        total_power
    )