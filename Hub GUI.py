import dearpygui.dearpygui as dpg  # Using Dear PyGui
import os
import subprocess
import threading
import time


########################################################################################################################
#                                               Add Device
########################################################################################################################

def addDevice(deviceId, code):
    print(f"Sending pair request to chip-tool: {deviceId}")

    script = "./addDevice.sh"

    expiration = 5 * 60

    process = subprocess.Popen(
        [script, deviceId, code], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    success = False

    try:
        # wait for the process to complete up to expiration
        output, error = process.communicate(timeout=expiration)

        # TODO: handle error

        # print the output, splitting it by \n
        lines = output.decode("utf-8").split('\n')
        for line in lines:
            print(line)

        # read temp-{deviceId}.txt
        with open(f"temp-{deviceId}.txt", "r") as f:
            fileLines = f.readlines()

            # check if any lines contain "error" regardless of case and is not errorCode=0
            for line in fileLines:
                if "error" in line.lower() and "errorCode=0" not in line and "Unsolicited msg with originator bit clear" not in line:
                    # delete temp.txt
                    try:
                        os.remove(f"temp-{deviceId}.txt")
                    except:
                        pass

                    print(f"Error: {line}")
                    return None

                if "Device commissioning completed with success" in line:
                    success = True

        # delete temp.txt
        try:
            os.remove(f"temp-{deviceId}.txt")
        except:
            pass
    except subprocess.TimeoutExpired as e:
        # delete temp.txt
        try:
            os.remove(f"temp-{deviceId}.txt")
        except:
            pass

        # get the process ID from the exception object
        pid = process.pid

        print(
            f"Timeout occurred. The command took longer than {expiration} seconds to execute. Killing process {pid}")

        # kill the process using the process ID
        subprocess.run(["kill", str(pid)])

        return None
    except Exception as e:
        # delete temp.txt
        try:
            os.remove(f"temp-{deviceId}.txt")
        except:
            pass

        print(f"Error: {e}")
        return None

    return success


def getDeviceType(deviceId):
    script = "./getDeviceType.sh"

    process = subprocess.Popen(
        [script, deviceId], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    deviceType = "sensor"

    try:
        # wait for the process to complete
        output, error = process.communicate()

        # print the output, splitting it by \n
        lines = output.decode("utf-8").split('\n')
        for line in lines:
            print(line)

        # read temp-{deviceId}.txt
        with open(f"temp-{deviceId}.txt", "r") as f:
            fileLines = f.readlines()

            # check if any lines contain "error" regardless of case
            for line in fileLines:
                if "error" in line.lower():
                    # delete temp.txt
                    try:
                        os.remove(f"temp-{deviceId}.txt")
                    except:
                        pass

                    print(f"Error: {line}")
                    return None

                if "UNSUPPORTED_CLUSTER" in line.upper():
                    deviceType = "actuator"
                    break

        # delete temp.txt
        try:
            os.remove(f"temp-{deviceId}.txt")
        except:
            pass
    except Exception as e:
        # delete temp.txt
        try:
            os.remove(f"temp-{deviceId}.txt")
        except:
            pass

        print(f"Error: {e}")
        return None

    return deviceType


########################################################################################################################
#                                               Get Sensor Data
########################################################################################################################

class SensorData:
    def __init__(self, temperature, humidity, pressure, soilMoisture, light):
        self.temperature = temperature
        self.humidity = humidity
        self.pressure = pressure
        self.soilMoisture = soilMoisture
        self.light = light


def getSensorData(deviceId):
    print(f"Sending data request to chip-tool: {deviceId}")

    script = "./getSensorData.sh"

    expiration = 20

    process = subprocess.Popen(
        [script, deviceId], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        # wait for the process to complete up to expiration
        output, error = process.communicate(timeout=expiration)

        # TODO: handle error

        # initialize empty SensorData object
        data = SensorData(None, None, None, None, None)

        # print the output, splitting it by \n
        lines = output.decode("utf-8").split('\n')
        for line in lines:
            print(line)

            # parse temperature with line containing "temperature: " and get value after space. store value in SensorData
            if "temperature: " in line:
                data.temperature = int(line.split("temperature: ")[1])
            if "humidity: " in line:
                data.moisture = int(line.split("humidity: ")[1])
            if "pressure: " in line:
                data.pressure = int(line.split("pressure: ")[1])
            if "soilMoisture: " in line:
                data.soilMoisture = int(line.split("soilMoisture: ")[1])
            if "light: " in line:
                data.pressure = int(line.split("light: ")[1])
    except subprocess.TimeoutExpired as e:
        # delete temp.txt
        try:
            os.remove(f"temp-{deviceId}.txt")
        except:
            pass

        # get the process ID from the exception object
        pid = process.pid

        print(
            f"Timeout occurred. The command took longer than {expiration} seconds to execute. Killing process {pid}")

        # kill the process using the process ID
        subprocess.run(["kill", str(pid)])

        return None
    except Exception as e:
        # delete temp.txt
        try:
            os.remove(f"temp-{deviceId}.txt")
        except:
            pass

        print(f"Error: {e}")
        return None

    return data


def getSensorDataTask(deviceId):
    # run a loop every 5 seconds
    while True:
        # get sensor data
        data = getSensorData(deviceId)

        if data is not None:
            print(f"Temperature: {data.temperature}")
            print(f"Humidity: {data.humidity}")
            print(f"Pressure: {data.pressure}")
            print(f"SoilMoisture: {data.soilMoisture}")
            print(f"Light: {data.light}")

        # NOTE: this sleep only occurs after getSensorData completes
        print("Waiting 5 seconds...")
        time.sleep(5)


########################################################################################################################
#                                               Remove Device
########################################################################################################################

def removeDevice(deviceId):
    print(f"Sending unpair request to chip-tool: {deviceId}")

    script = "./removeDevice.sh"

    expiration = 10

    process = subprocess.Popen(
        [script, deviceId], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        # wait for the process to complete up to expiration
        output, error = process.communicate(timeout=expiration)

        # TODO: handle error

        # print the output, splitting it by \n
        lines = output.decode("utf-8").split('\n')
        for line in lines:
            print(line)

        # read temp-{deviceId}.txt
        with open(f"temp-{deviceId}.txt", "r") as f:
            fileLines = f.readlines()

            # check if any lines contain "error" regardless of case
            for line in fileLines:
                if "error" in line.lower():
                    # delete temp.txt
                    try:
                        os.remove(f"temp-{deviceId}.txt")
                    except:
                        pass

                    print(f"Error: {line}")
                    return None

        # delete temp.txt
        try:
            os.remove(f"temp-{deviceId}.txt")
        except:
            pass

        # delete row in nodeIds.csv that contains deviceId
        with open("../nodeIds.csv", "r") as f:
            fileLines = f.readlines()

        with open("../nodeIds.csv", "w") as f:
            for line in fileLines:
                # deviceId is first column
                if line.strip().split(",")[0] != deviceId:
                    f.write(line)

    except subprocess.TimeoutExpired as e:
        # delete temp.txt
        try:
            os.remove(f"temp-{deviceId}.txt")
        except:
            pass

        # get the process ID from the exception object
        pid = process.pid

        print(
            f"Timeout occurred. The command took longer than {expiration} seconds to execute. Killing process {pid}")

        # kill the process using the process ID
        subprocess.run(["kill", str(pid)])

        return None
    except Exception as e:
        # delete temp.txt
        try:
            os.remove(f"temp-{deviceId}.txt")
        except:
            pass

        print(f"Error: {e}")
        return None

    return True


########################################################################################################################
#                                               Hub GUI Code
########################################################################################################################

dpg.create_context()
# dpg.show_style_editor()

# Dictionary that holds Node data
nodeList = {
    "Name": [],
    "Temperature": [],
    "Humidity": []
}

# Reading in saved name values
if os.stat("name.txt").st_size == 0:
    data_into_list1 = []
else:
    with open('name.txt', 'r') as name_file:
        data_name = name_file.read()
        data_into_list1 = data_name.splitlines()
        for item in data_into_list1:
            nodeList["Name"].append(item)

# Reading in saved temperature values
if os.stat("temperature.txt").st_size == 0:
    data_into_list2 = []
else:
    with open('temperature.txt', 'r') as temperature_file:
        data_name = temperature_file.read()
        data_into_list2 = data_name.splitlines()
        for item in data_into_list2:
            nodeList["Temperature"].append(item)

# Reading in saved humidity values
if os.stat("humidity.txt").st_size == 0:
    data_into_list3 = []
else:
    with open('humidity.txt', 'r') as humidity_file:
        data_name = humidity_file.read()
        data_into_list3 = data_name.splitlines()
        for item in data_into_list3:
            nodeList["Humidity"].append(item)


#class SavedNodes:
    #def __init__(self, name, temperature, humidity):
        #self.name = name
        #self.temperature = temperature
        #self.humidity = humidity


########################################################################################################################
#                                               Themes and Fonts
########################################################################################################################

# List of available Fonts that can be used
with dpg.font_registry():
    main_font = dpg.add_font("OpenSans-Regular.ttf", 30)

# Global Theme
with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 0, 0), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (255, 255, 255), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Button, (77, 182, 255), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 0, 0), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (77, 182, 255), category=dpg.mvThemeCat_Core)

        dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 12, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1, category=dpg.mvThemeCat_Core)

# Input Text Field Theme
with dpg.theme() as input_text_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 0, 0), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (77, 182, 255), category=dpg.mvThemeCat_Core)

# Theme for Listbox on Home Page
with dpg.theme() as listbox_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 0, 0), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (77, 182, 255), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (77, 182, 255), category=dpg.mvThemeCat_Core)

        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 0, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1, category=dpg.mvThemeCat_Core)

with dpg.theme() as test_button_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 0, 0), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Button, (255, 10, 10), category=dpg.mvThemeCat_Core)


########################################################################################################################
#                                                Callbacks
########################################################################################################################

# Functionality of the "Go Back" Button
def go_back_callback(sender, app_data, user_data):
    dpg.set_primary_window("Home Window", True)
    dpg.hide_item("New Device Window")
    dpg.hide_item("Statistics Window")
    dpg.show_item("Home Window")


# Functionality of the "+ Add New Device" Button
def add_new_device(sender, app_data, user_data):
    dpg.set_primary_window("New Device Window", True)
    dpg.hide_item("Home Window")
    dpg.show_item("New Device Window")


# Functionality of the "Add" Button on the New Device Window
def add_device_callback(sender, app_data, user_data):
    code = dpg.get_value("Input")

    print(f"Pairing code: {code}")

    # read nodeIds.csv
    with open("./nodeIds.csv", "r") as f:
        fileLines = f.readlines()

        # remove all empty lines
        fileLines = [line for line in fileLines if line.strip() != ""]

        # get next nodeId. if file is empty, use 1
        if len(fileLines) == 0:
            nodeId = 1
        else:
            nodeId = int(fileLines[-1].split(",")[0]) + 1

        # check if nodeId already exists. if it does, keep incrementing until it doesn't
        while True:
            if any(str(nodeId) in line for line in fileLines):
                nodeId += 1
            else:
                break

        deviceId = str(nodeId)

        print(f"Adding device with deviceId: {deviceId}")

        success = addDevice(deviceId, code)
        if success is not None and success == True:
            # get device type
            print(f"Getting device type for {deviceId}")
            deviceType = getDeviceType(deviceId)

            if deviceType is not None:
                print(f"Device added successfully: {deviceId}, {deviceType}")

                # write nodeId to file on the next line
                with open("../nodeIds.csv", "a") as f:
                    f.write(f"{deviceId},{deviceType}\n")

    if not success:
        print("Fail")
        pass
    else:
        dpg.set_primary_window("Home Window", True)
        dpg.hide_item("New Device Window")
        dpg.show_item("Home Window")
        nodeList["Name"].append(deviceId)
        dpg.configure_item(allNodes, items=nodeList["Name"])
        nodeList["Temperature"].append("0")
        nodeList["Humidity"].append("0")


# Functionality for when an item in the main list box is pressed
def list_callback(sender, app_data, user_data):
    name = nodeList["Name"]
    temp = nodeList["Temperature"]
    humidity = nodeList["Humidity"]
    index = name.index(dpg.get_value(sender))
    print(dpg.get_value(sender))
    print(nodeList["Temperature"])
    print(nodeList["Humidity"])

    dpg.configure_item(name_data, default_value=dpg.get_value(sender))
    dpg.configure_item(temperature_data, default_value=temp[index])
    dpg.configure_item(humidity_data, default_value=humidity[index])


# Functionality for "set statistics" button
def statistics_window(sender, app_data, user_data):
    dpg.set_primary_window("Statistics Window", True)
    dpg.show_item("Statistics Window")
    dpg.hide_item("Home Window")


# Functionality for the save button in the statistics window
def save_statistics(sender, app_data, user_data):
    newname = dpg.get_value(user_data[0])
    if not newname:
        pass
    else:
        if newname not in nodeList["Name"]:
            nodeList["Name"].append(newname)
            nodeList["Temperature"].append(dpg.get_value(user_data[1]))
            nodeList["Humidity"].append(dpg.get_value(user_data[2]))
            dpg.configure_item(allNodes, items=nodeList["Name"])
        else:
            name = nodeList["Name"]
            temp = nodeList["Temperature"]
            humidity = nodeList["Humidity"]
            index = name.index(newname)
            temp[index] = dpg.get_value(user_data[1])
            humidity[index] = dpg.get_value(user_data[2])


# Functionality for the "print" button
def print_node(sender, app_data, user_data):
    print(nodeList)
    name_values = nodeList["Name"]
    temperature_values = nodeList["Temperature"]
    humidity_values = nodeList["Humidity"]
    with open('name.txt', 'w') as file:
        for item in name_values:
            file.write(str(item).replace("'", "") + "\n")

    with open('temperature.txt', 'w') as file:
        for item in temperature_values:
            file.write(str(item).replace("'", "") + "\n")

    with open('humidity.txt', 'w') as file:
        for item in humidity_values:
            file.write(str(item).replace("'", "") + "\n")

    deviceId = "4"

    #run getSensorDataTask in a background thread
    t = threading.Thread(target=getSensorDataTask, args=(deviceId,))
    t.start()

    # optional: wait for thread to finish
    t.join()


########################################################################################################################
#                                                Windows
########################################################################################################################


# Home Window
with dpg.window(tag="Home Window", width=800, height=450):
    dpg.draw_line((0, 50), (800, 50), thickness=5, color=(77, 182, 255))

    # Header Text
    t1 = dpg.add_text("Home", pos=(10, 10))
    dpg.bind_item_font(t1, main_font)

    # Add New Device Button
    b2 = dpg.add_button(label="+ Add New Device", small=True, pos=(580, 10), callback=add_new_device)
    dpg.bind_item_font(b2, main_font)

    # Node Listbox
    allNodes = dpg.add_listbox(items=nodeList["Name"], tag="Nodes", pos=(100, 100), width=600, num_items=3,
                               callback=list_callback)
    dpg.bind_item_font(allNodes, main_font)

    # Titles for statistics
    name = dpg.add_text("Name:", pos=(10, 220))
    dpg.bind_item_font(name, main_font)
    temperature = dpg.add_text("Temperature:", pos=(10, 270))
    dpg.bind_item_font(temperature, main_font)
    humidity = dpg.add_text("Humidity:", pos=(10, 320))
    dpg.bind_item_font(humidity, main_font)

    # Data for statistics
    name_data = dpg.add_text("0", pos=(90, 220))
    dpg.bind_item_font(name_data, main_font)
    temperature_data = dpg.add_text("0", pos=(160, 270))
    dpg.bind_item_font(temperature_data, main_font)
    humidity_data = dpg.add_text("0", pos=(120, 320))
    dpg.bind_item_font(humidity_data, main_font)

    # Temporary Test Buttons
    statistics_button = dpg.add_button(label="Set Statistics", small=True, pos=(200, 10), callback=statistics_window)
    dpg.bind_item_font(statistics_button, main_font)
    print_button = dpg.add_button(label="print", small=True, pos=(400, 10), callback=print_node)
    dpg.bind_item_font(print_button, main_font)

# New Device Window
with dpg.window(tag="New Device Window"):
    dpg.draw_line((0, 50), (800, 50), thickness=5, color=(77, 182, 255))

    # Header Text
    new_device_header = dpg.add_text("Add New Device", pos=(10, 10))
    dpg.bind_item_font(new_device_header, main_font)

    # Go Back Button
    go_back_button = dpg.add_button(label="Go Back", width=300, height=100, pos=(680, 10), small=True,
                                    callback=go_back_callback)
    dpg.bind_item_font(go_back_button, main_font)

    # Input Text Field
    new_device_input = dpg.add_input_text(tag="Input", label="Enter Pairing Code", pos=(212, 200), width=200)
    dpg.bind_item_font(new_device_input, main_font)

    # Add Device Button
    add_device_button = dpg.add_button(label="Add", width=150, height=50, pos=(325, 250), callback=add_device_callback)
    dpg.bind_item_font(add_device_button, main_font)

# Statistics Window
with dpg.window(tag="Statistics Window", width=800, height=450):
    dpg.draw_line((0, 50), (800, 50), thickness=5, color=(77, 182, 255))

    # Header Text
    title = dpg.add_text("Statistics Window", pos=(10, 10))
    dpg.bind_item_font(title, main_font)

    # Go Back Button
    go_back_button = dpg.add_button(label="Go Back", width=300, height=100, pos=(680, 10), small=True,
                                    callback=go_back_callback)
    dpg.bind_item_font(go_back_button, main_font)

    # Statistic Inputs
    name = dpg.add_input_text(label="Name", pos=(10, 100))
    dpg.bind_item_font(name, main_font)
    temperature = dpg.add_input_float(label="Temperature", pos=(10, 150))
    dpg.bind_item_font(temperature, main_font)
    humidity = dpg.add_input_float(label="Humidity", pos=(10, 200))
    dpg.bind_item_font(humidity, main_font)

    # Save Statistics Button
    save_button = dpg.add_button(label="Save", width=300, height=100, pos=(350, 250), small=True,
                                 user_data=[name, temperature, humidity], callback=save_statistics)
    dpg.bind_item_font(save_button, main_font)

dpg.configure_item(allNodes, items=nodeList["Name"])

# Binding themes to items
dpg.bind_theme(global_theme)
dpg.bind_item_theme(allNodes, listbox_theme)
dpg.bind_item_theme(new_device_input, input_text_theme)
dpg.bind_item_theme(statistics_button, test_button_theme)
dpg.bind_item_theme(print_button, test_button_theme)

dpg.create_viewport(title='Hub GUI', width=800, height=480)
dpg.setup_dearpygui()
dpg.show_viewport()
# dpg.toggle_viewport_fullscreen()
dpg.set_primary_window("Home Window", True)
dpg.hide_item("New Device Window")
dpg.hide_item("Statistics Window")
dpg.start_dearpygui()
dpg.destroy_context()

# dpg.draw_rectangle((0, 0), (800, 50), fill=(77, 182, 255))
# dpg.draw_line((0, 50), (800, 50), thickness=5, color=(77, 182, 255))
# dpg.save_init_file("Gui.ini")
