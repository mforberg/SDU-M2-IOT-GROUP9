$(document).ready(function () {
    $("#updateButton").click(function () {
        $.ajax({
            type: "GET",
            url: '/hiddenFunctionality/',
            dataType: 'json',
            data: {
                functionname: 'updateData'
            },

            success: function (obj) {
                if (!('error' in obj)) {
                    visualize_2D_plot(obj);
                }
                else {
                    console.log(obj.error);
                }
            },
            error: function (xhr, textStatus, errorThrown) {
                console.log('STATUS: ' + textStatus + '\nERROR THROWN: ' + errorThrown);
            }
        });
    });

    $("#rgbSender").click(function () {
        $.ajax({
            type: "GET",
            url: '/hiddenFunctionality/',
            dataType: 'json',
            data: {
                functionname: 'changeRGB',
                variable: document.getElementById("color").value
            },

            success: function (obj) {
                if (!('error' in obj)) {
                    console.log(obj);
                }
                else {
                    console.log(obj.error);
                }
            },
            error: function (xhr, textStatus, errorThrown) {
                console.log('STATUS: ' + textStatus + '\nERROR THROWN: ' + errorThrown);
            }
        });
    });

    $("#setIntensity").click(function () {
        $.ajax({
            type: "GET",
            url: '/hiddenFunctionality/',
            dataType: 'json',
            data: {
                functionname: 'setIntensity',
                variable: document.getElementById("intensity").value
            },

            success: function (obj) {
                if (!('error' in obj)) {
                    console.log(obj);
                }
                else {
                    console.log(obj.error);
                }
            },
            error: function (xhr, textStatus, errorThrown) {
                console.log('STATUS: ' + textStatus + '\nERROR THROWN: ' + errorThrown);
            }
        });
    });

    $("#setSetPoint").click(function () {
        $.ajax({
            type: "GET",
            url: '/hiddenFunctionality/',
            dataType: 'json',
            data: {
                functionname: 'setSetPoint',
                variable: document.getElementById("setpoint").value
            },

            success: function (obj) {
                if (!('error' in obj)) {
                    console.log(obj);
                }
                else {
                    console.log(obj.error);
                }
            },
            error: function (xhr, textStatus, errorThrown) {
                console.log('STATUS: ' + textStatus + '\nERROR THROWN: ' + errorThrown);
            }
        });
    });
});
