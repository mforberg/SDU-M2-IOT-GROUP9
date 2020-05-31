from flask import Flask, request, render_template
import json

import communication.clientClass as cC

app = Flask(__name__)
thing = cC.ClientClass()


@app.route('/')
def index():
    return render_template("visualization.html")


@app.route('/hiddenFunctionality/', methods=['GET'])
def dippers():
    if request.method == "GET":
        try:
            func = request.args.get('functionname')
            var = request.args.get('variable')
            if func == "updateData":
                data = get_data()
                return json.dumps(data)
            elif func == "changeRGB":
                thing.deliver_payload(var.replace("#", "0x"), "sdu/iot/gruppe9/rgb")
                return json.dumps({"success": "rgbChanged"})
            elif func == "setIntensity":
                thing.deliver_payload(var, "sdu/iot/gruppe9/intensity")
                return json.dumps({"success": "setIntensity"})
            elif func == "setSetPoint":
                thing.deliver_payload(var, "sdu/iot/gruppe9/setpoint")
                return json.dumps({"success": "setSetPoint"})
        except Exception as e:
            return e


def get_data():
    data = []
    with open("communication/data.csv", "r") as file:
        for line in file:
            stripped_line = line.replace("\n", "")
            line_dict = json.loads(stripped_line)
            if len(line_dict) == 6:
                if {"mode", "light", "var", "time", "name", "timeAfter"} == set(line_dict):
                    inner_map = {"mode": line_dict["mode"], "light": line_dict["light"], "var": line_dict["var"],
                                 "time": line_dict["time"], "name": line_dict["name"]}
                    data.append(inner_map)
    return data


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="8080", debug=True)
