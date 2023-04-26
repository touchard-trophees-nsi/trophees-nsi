
start_code = ''
update_code = ''
end_code = ''

isDeviceRunning = False

def set_code(start, update, end):
    global start_code,update_code,end_code
    start_code = start
    update_code = update
    end_code = end

def get_code():
    global start_code,update_code,end_code
    return start_code,update_code,end_code

def set_game_state(state):
    global isDeviceRunning
    isDeviceRunning = state

def get_game_state():
    global isDeviceRunning
    return isDeviceRunning