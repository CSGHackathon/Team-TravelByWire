statusTimer()
var myVar = setInterval(statusTimer, 1000);
states = null;

function statusTimer() {
    $.get( "/status", function( data ) {
        console.log("state: " + data)
        states = JSON.parse(data);
        for (var device in states) {
            state = states[device];
            if (state == true){
                $("#"+ device).removeClass("off")
                $("#"+ device).addClass("on")
            }else{
                $("#"+ device).removeClass("on")
                $("#"+ device).addClass("off")
            }
        }
    });
}

function toggle(device){
    console.log("Toggling: " + device)
    var new_state = null;
    if (states[device] == true){
        new_state = "off"
    }else{
        new_state = "on"
    }

    $.get( "/toggle?device=" + device + "&state=" + new_state);
}
