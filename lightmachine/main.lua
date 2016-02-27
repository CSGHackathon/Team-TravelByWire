gpio.mode(0,gpio.OUTPUT)
gpio.write(0,gpio.LOW)

is_on = false

srv = net.createServer(net.TCP, 30)
srv:listen(80,function(conn)
    conn:on('receive', function(conn,payload)
        conn:send('HTTP/1.1 200 OK\n\n')
        query = string.match(payload,"GET%s+%S+")
        print(query)
        if string.find(query,"GET /on") then
            is_on = true
            gpio.write(0,gpio.HIGH)
        elseif string.find(query,"GET /off") then
            is_on = false
            gpio.write(0,gpio.LOW)
        end

        if is_on then
            conn:send('on')
        else
            conn:send('off')
        end
        conn:on('sent',function(conn) conn:close() end)
    end)
end)
