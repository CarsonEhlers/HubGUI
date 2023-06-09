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
    "Humidity": [],
    "Pressure": [],
    "Moisture": [],
    "Light": [],
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

# Reading in saved pressure values
if os.stat("pressure.txt").st_size == 0:
    data_into_list4 = []
else:
    with open('pressure.txt', 'r') as name_file:
        data_name = name_file.read()
        data_into_list4 = data_name.splitlines()
        for item in data_into_list4:
            nodeList["Pressure"].append(item)

# Reading in saved moisture values
if os.stat("moisture.txt").st_size == 0:
    data_into_list5 = []
else:
    with open('moisture', 'r') as name_file:
        data_name = name_file.read()
        data_into_list5 = data_name.splitlines()
        for item in data_into_list5:
            nodeList["Moisture"].append(item)

# Reading in saved light values
if os.stat("light.txt").st_size == 0:
    data_into_list6 = []
else:
    with open('light', 'r') as name_file:
        data_name = name_file.read()
        data_into_list6 = data_name.splitlines()
        for item in data_into_list6:
            nodeList["Light"].append(item)

########################################################################################################################
#                                               Themes and Fonts
########################################################################################################################

# List of available Fonts that can be used
with dpg.font_registry():
    main_font = dpg.add_font("OpenSans-Regular.ttf", 40)

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
        nodeList["Pressure"].append("0")
        nodeList["Moisture"].append("0")
        nodeList["Light"].append("0")


# Functionality for when an item in the main list box is pressed
def list_callback(sender, app_data, user_data):
    name = nodeList["Name"]
    temp = nodeList["Temperature"]
    humidity = nodeList["Humidity"]
    pressure = nodeList["Pressure"]
    moisture = nodeList["Moisture"]
    light = nodeList["Light"]
    index = name.index(dpg.get_value(sender))
    print(dpg.get_value(sender))
    print(nodeList["Temperature"])
    print(nodeList["Humidity"])
    print(nodeList["Pressure"])
    print(nodeList["Moisture"])
    print(nodeList["Light"])

    dpg.configure_item(name_data, default_value=dpg.get_value(sender))
    dpg.configure_item(temperature_data, default_value=temp[index])
    dpg.configure_item(humidity_data, default_value=humidity[index])
    dpg.configure_item(pressure_data, default_value=pressure[index])
    dpg.configure_item(moisture_data, default_value=moisture[index])
    dpg.configure_item(light_data, default_value=light[index])


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
            nodeList["Pressure"].append(dpg.get_value(user_data[3]))
            nodeList["Moisture"].append(dpg.get_value(user_data[4]))
            nodeList["Light"].append(dpg.get_value(user_data[5]))
            dpg.configure_item(allNodes, items=nodeList["Name"])
        else:
            name = nodeList["Name"]
            temp = nodeList["Temperature"]
            humidity = nodeList["Humidity"]
            pressure = nodeList["Pressure"]
            moisture = nodeList["Moisture"]
            light = nodeList["Light"]
            index = name.index(newname)
            temp[index] = dpg.get_value(user_data[1])
            humidity[index] = dpg.get_value(user_data[2])
            pressure[index] = dpg.get_value(user_data[3])
            moisture[index] = dpg.get_value(user_data[4])
            light[index] = dpg.get_value(user_data[5])

########################################################################################################################
#                                                Windows
########################################################################################################################


# Home Window
with dpg.window(tag="Home Window", width=1920, height=1080):
    dpg.draw_line((0, 80), (1080, 80), thickness=10, color=(77, 182, 255))

    # Header Text
    t1 = dpg.add_text("Home", pos=(20, 20))
    dpg.bind_item_font(t1, main_font)

    # Add New Device Button
    b2 = dpg.add_button(label="+ Add New Device", small=True, pos=(800, 20), callback=add_new_device)
    dpg.bind_item_font(b2, main_font)

    # Node Listbox
    allNodes = dpg.add_listbox(items=nodeList["Name"], tag="Nodes", pos=(190, 120), width=700, num_items=3,
                               callback=list_callback)
    dpg.bind_item_font(allNodes, main_font)

    # Titles for statistics
    name = dpg.add_text("Name:", pos=(20, 300))
    dpg.bind_item_font(name, main_font)
    temperature = dpg.add_text("Temperature:", pos=(20, 380))
    dpg.bind_item_font(temperature, main_font)
    humidity = dpg.add_text("Humidity:", pos=(20, 460))
    dpg.bind_item_font(humidity, main_font)
    pressure_title = dpg.add_text("Air Pressure:", pos=(20, 540))
    dpg.bind_item_font(pressure_title, main_font)
    moisture_title = dpg.add_text("Soil Moisture:", pos=(20, 620))
    dpg.bind_item_font(moisture_title, main_font)
    light_title = dpg.add_text("Light Level:", pos=(20, 700))
    dpg.bind_item_font(light_title, main_font)

    # Data for statistics
    name_data = dpg.add_text("", pos=(300, 300))
    dpg.bind_item_font(name_data, main_font)
    temperature_data = dpg.add_text("", pos=(300, 380))
    dpg.bind_item_font(temperature_data, main_font)
    humidity_data = dpg.add_text("", pos=(300, 460))
    dpg.bind_item_font(humidity_data, main_font)
    pressure_data = dpg.add_text("", pos=(300, 540))
    dpg.bind_item_font(pressure_data, main_font)
    moisture_data = dpg.add_text("", pos=(300, 620))
    dpg.bind_item_font(moisture_data, main_font)
    light_data = dpg.add_text("", pos=(300, 700))
    dpg.bind_item_font(light_data, main_font)

    # Temporary Test Buttons
    statistics_button = dpg.add_button(label="Set Statistics", small=True, pos=(250, 20), callback=statistics_window)
    dpg.bind_item_font(statistics_button, main_font)

# New Device Window
with dpg.window(tag="New Device Window"):
    dpg.draw_line((0, 80), (1080, 80), thickness=10, color=(77, 182, 255))

    # Header Text
    new_device_header = dpg.add_text("Add New Device", pos=(20, 20))
    dpg.bind_item_font(new_device_header, main_font)

    # Go Back Button
    go_back_button = dpg.add_button(label="Go Back", width=675, height=225, pos=(950, 20), small=True,
                                    callback=go_back_callback)
    dpg.bind_item_font(go_back_button, main_font)

    # Input Text Field
    new_device_input = dpg.add_input_text(tag="Input", label="Enter Pairing Code", pos=(530, 600), width=600)
    dpg.bind_item_font(new_device_input, main_font)

    # Add Device Button
    add_device_button = dpg.add_button(label="Add", width=337, height=112, pos=(805, 750), callback=add_device_callback)
    dpg.bind_item_font(add_device_button, main_font)

# Statistics Window
with dpg.window(tag="Statistics Window", width=1080, height=800):
    dpg.draw_line((0, 80), (1080, 80), thickness=10, color=(77, 182, 255))

    # Header Text
    title = dpg.add_text("Statistics Window", pos=(20, 20))
    dpg.bind_item_font(title, main_font)

    # Go Back Button
    go_back_button = dpg.add_button(label="Go Back", width=675, height=225, pos=(950, 20), small=True,
                                    callback=go_back_callback)
    dpg.bind_item_font(go_back_button, main_font)

    # Statistic Inputs
    name = dpg.add_input_text(label="Name", pos=(20, 200))
    dpg.bind_item_font(name, main_font)
    temperature = dpg.add_input_float(label="Temperature", pos=(20, 300))
    dpg.bind_item_font(temperature, main_font)
    humidity = dpg.add_input_float(label="Humidity", pos=(20, 400))
    dpg.bind_item_font(humidity, main_font)
    pressure = dpg.add_input_float(label="Pressure", pos=(20, 500))
    dpg.bind_item_font(pressure, main_font)
    soil_moisture = dpg.add_input_float(label="Soil Moisture", pos=(20, 600))
    dpg.bind_item_font(soil_moisture, main_font)
    light = dpg.add_input_float(label="Light", pos=(20, 700))
    dpg.bind_item_font(light, main_font)

    # Save Statistics Button
    save_button = dpg.add_button(label="Save", width=675, height=225, pos=(1000, 800), small=True,
                                 user_data=[name, temperature, humidity, pressure, soil_moisture, light],
                                 callback=save_statistics)
    dpg.bind_item_font(save_button, main_font)

dpg.configure_item(allNodes, items=nodeList["Name"])

# Binding themes to items
dpg.bind_theme(global_theme)
dpg.bind_item_theme(allNodes, listbox_theme)
dpg.bind_item_theme(new_device_input, input_text_theme)
dpg.bind_item_theme(statistics_button, test_button_theme)

dpg.create_viewport(title='Hub GUI', width=1920, height=1080)
dpg.setup_dearpygui()
dpg.show_viewport()
# dpg.toggle_viewport_fullscreen()
dpg.set_primary_window("Home Window", True)
dpg.hide_item("New Device Window")
dpg.hide_item("Statistics Window")
dpg.start_dearpygui()
dpg.destroy_context()

