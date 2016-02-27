var myVar = setInterval(statusTimer, 2000);

function statusTimer() {
    $.get( "/status", function( data ) {
        console.log("status msg")
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
