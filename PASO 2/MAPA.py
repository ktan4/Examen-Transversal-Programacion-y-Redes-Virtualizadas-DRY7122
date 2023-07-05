import tkinter as tk
from tkinter import scrolledtext
import urllib.parse
import requests

main_api = "https://www.mapquestapi.com/directions/v2/route?"
key = "LWPG7pOaoqiPjZeYV8lFY3z3hIP3DI3X"
locale = "es_MX"
unit = "k"
avoids = "Toll Road"
routeType = "fastest"
directions_open = False  # Variable para verificar si se han abierto las indicaciones

def get_directions():
    global directions_open
    
    orig = orig_entry.get()
    dest = dest_entry.get()
    vehicle_type = vehicle_var.get()

    # Mapear los valores seleccionados a los nombres en español
    vehicle_map = {
        "car": "auto",
        "motorcycle": "motocicleta",
        "walking": "caminando",
        "bus": "autobús",
        "bicycle": "bicicleta"
    }
    vehicle_name = vehicle_map.get(vehicle_type, "")

    if not vehicle_name:
        result_text.set("Tipo de vehículo inválido")
        return

    url = main_api + urllib.parse.urlencode(
        {"key": key, "locale": locale, "unit": unit, "from": orig, "to": dest, "avoids": avoids, "routeType": routeType})
    json_data = requests.get(url).json()
    json_status = json_data["info"]["statuscode"]
    if json_status == 0:
        duration = json_data["route"]["formattedTime"]
        distance = "{:.3f}".format(json_data["route"]["distance"])

        # Calcular el combustible requerido según el tipo de vehículo
        if vehicle_type == "car":
            mileage = 12.5  # Ejemplo de kilometraje para un auto
        elif vehicle_type == "motorcycle":
            mileage = 20.0  # Ejemplo de kilometraje para una motocicleta
        elif vehicle_type == "walking":
            mileage = 0.0  # Sin consumo de combustible al caminar
        elif vehicle_type == "bus":
            mileage = 5.0  # Ejemplo de consumo de combustible para un autobús
        elif vehicle_type == "bicycle":
            mileage = 0.0  # Sin consumo de combustible en bicicleta
        else:
            result_text.set("Tipo de vehículo inválido")
            return

        fuel_required = round(float(distance) / mileage, 3)

        open_directions_window(orig, dest, duration, distance, fuel_required, json_data["route"]["legs"][0]["maneuvers"],
                               vehicle_name)
    elif json_status == 402:
        result_text.set("Status Code: " + str(json_status) + "; No se ha ingresado un Origen o Destino Válido.")
    elif json_status == 611:
        result_text.set("Status Code: " + str(json_status) + "; Falta Ingresar Origen o Destino.")
    else:
        result_text.set("For Staus Code: " + str(json_status) + "; Refer to:\n" +
                        "https://developer.mapquest.com/documentation/directions-api/status-codes")


def open_directions_window(orig, dest, duration, distance, fuel_required, maneuvers, vehicle_name):
    global directions_open

    directions_window = tk.Toplevel(window)
    directions_window.title("Indicaciones")

    orig_label = tk.Label(directions_window, text="Origen: " + orig)
    orig_label.pack()

    dest_label = tk.Label(directions_window, text="Destino: " + dest)
    dest_label.pack()

    duration_label = tk.Label(directions_window, text="Duración del Viaje: " + duration)
    duration_label.pack()

    distance_label = tk.Label(directions_window, text="Total en Kilómetros: " + str(distance))
    distance_label.pack()

    fuel_label = tk.Label(directions_window, text="Combustible Requerido: " + "{:.3f}".format(fuel_required) + " litros")
    fuel_label.pack()

    vehicle_label = tk.Label(directions_window, text="Tipo de vehículo: " + vehicle_name)
    vehicle_label.pack()

    maneuvers_label = tk.Label(directions_window, text="Instrucciones:")
    maneuvers_label.pack()

    maneuvers_text = scrolledtext.ScrolledText(directions_window, width=40, height=10)
    maneuvers_text.pack()

    for maneuver in maneuvers:
        maneuvers_text.insert(tk.END, maneuver["narrative"] + "\n")

    directions_open = True  # Indicaciones abiertas


def exit_program(event):
    global directions_open

    if event.char.lower() == 'q' and directions_open:
        window.quit()


window = tk.Tk()
window.title("Navegación a través de Mapquest")

orig_label = tk.Label(window, text="Lugar de Origen:")
orig_label.grid(row=0, column=0, padx=5, pady=5)

orig_entry = tk.Entry(window)
orig_entry.grid(row=0, column=1, padx=5, pady=5)

dest_label = tk.Label(window, text="Destino:")
dest_label.grid(row=1, column=0, padx=5, pady=5)

dest_entry = tk.Entry(window)
dest_entry.grid(row=1, column=1, padx=5, pady=5)

vehicle_label = tk.Label(window, text="Tipo de vehículo:")
vehicle_label.grid(row=2, column=0, padx=5, pady=5)

vehicle_var = tk.StringVar()
vehicle_checkbuttons = [
    ("Auto", "car"),
    ("Motocicleta", "motorcycle"),
    ("Caminando", "walking"),
    ("Autobús", "bus"),
    ("Bicicleta", "bicycle")
]

for i, (text, value) in enumerate(vehicle_checkbuttons):
    checkbutton = tk.Checkbutton(window, text=text, variable=vehicle_var, onvalue=value, offvalue="")
    checkbutton.grid(row=i + 2, column=1, sticky="w")

submit_button = tk.Button(window, text="Buscar", command=get_directions)
submit_button.grid(row=7, column=0, columnspan=2, padx=5, pady=5)

result_text = tk.StringVar()
result_label = tk.Label(window, textvariable=result_text, justify=tk.LEFT)
result_label.grid(row=8, column=0, columnspan=2, padx=5, pady=5)

window.bind("<Key>", exit_program)
window.mainloop()