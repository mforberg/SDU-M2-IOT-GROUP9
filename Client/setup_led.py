obs_min = 49
increment = 10.4375
obs_max = 216

def find_led(setpoint):

    if setpoint < obs_min+increment:
        current_led = 0
    elif setpoint < obs_min+increment*2:
        current_led = 1
    elif setpoint < obs_min+increment*3:
        current_led = 2
    elif setpoint < obs_min+increment*4:
        current_led = 3
    elif setpoint < obs_min+increment*5:
        current_led = 4
    elif setpoint < obs_min+increment*6:
        current_led = 5
    elif setpoint < obs_min+increment*7:
        current_led = 6
    elif setpoint < obs_min+increment*8:
        current_led = 7
    elif setpoint < obs_min+increment*9:
        current_led = 8
    elif setpoint < obs_min+increment*10:
        current_led = 9
    elif setpoint < obs_min+increment*11:
        current_led = 10
    elif setpoint < obs_min+increment*12:
        current_led = 11
    elif setpoint < obs_min+increment*13:
        current_led = 12
    elif setpoint < obs_min+increment*14:
        current_led = 13
    elif setpoint < obs_min+increment*15:
        current_led = 14
    else:
        current_led = 15
    return current_led