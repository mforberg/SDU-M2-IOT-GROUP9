function visualize_2D_plot(thingies){
    // convert to the format of the example
    let exampleFormat = [];

    for (let i = 1; i < thingies.length; i++){
        let inner = {};
        let inner2 = {};
        if (thingies[i]['mode'] === "MANUAL"){
            inner['time'] = parseInt(thingies[i]['time']);
            inner['light'] = parseInt(thingies[i]['light']);
            inner['category'] = "Manual-" + thingies[i]['var'];
            exampleFormat.push(inner);
        } else if (thingies[i]['mode'] === "RGB") {
            inner['time'] = parseInt(thingies[i]['time']);
            inner['light'] = parseInt(thingies[i]['light']);
            inner['category'] = "RGB";
            exampleFormat.push(inner);
        } else {
            inner['time'] = parseInt(thingies[i]['time']);
            inner['light'] = parseInt(thingies[i]['light']);
            inner['category'] = "Light";
            exampleFormat.push(inner);
            inner2['time'] = parseInt(thingies[i]['time']);
            inner2['light'] = parseInt(thingies[i]['var']);
            inner2['category'] = "Setpoint";
            exampleFormat.push(inner2);
        }

    }

    let jsonData = JSON.stringify(exampleFormat);

    let yourVlSpec = {
        "width": "container",
        "$schema": "https://vega.github.io/schema/vega-lite/v4.json",
        "description": "A scatterplot showing time and light level for each reading.",
        "data": {
            "values": jsonData
        },
        "selection": {
            "grid": {
                "type": "interval", "bind": "scales",
                "zoom": "wheel![event.shiftKey]"
            }
        },
        "mark": {"type":"circle", "tooltip": true},
        "encoding": {
            "x": {"field": "time", "type": "temporal", "axis": {"title": "Timestamp"}},
            "y": {"field": "light", "type": "quantitative", "axis": {"title": "Light Level (Lumen)"}},
            "color": {"field": "category", "type": "nominal"}
        }
    };
    vegaEmbed('#vis', yourVlSpec);
}