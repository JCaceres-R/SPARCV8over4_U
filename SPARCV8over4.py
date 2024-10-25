#Falta convertir valores registros y  mem en hexa
#Mem y registros repetidos Quitar uno
#ordenar registros y memoria

import network
import socket
import ure
import json
import time


#BACKEND MEM#########################
import array
import uctypes

memory={}

struct_32 = {
    "value": uctypes.UINT32 | 0  # UINT32 es un entero sin signo de 32 bits, y 0 es el offset en la estructura
}

def get_uctype(address):
    if  address not in memory:
        memory[address]=uctypes.struct(address, struct_32)
    return memory[address]



   
    
def read_memory(address,rd):
    assert address % 4 == 0, f"The address {address} is not divisible by 4."
    print('read_memory',address)
    return get_uctype(address).value

def write_memory(address,data):
    assert address % 4 == 0, f"The address {address} is not divisible by 4."
    print( 'write_memory',address,data)
    get_uctype(address).value=data
     
 

def malloc(num_bytes,rd):
    assert num_bytes % 4 == 0, f"The number {num_bytes} is not divisible by 4."
    buff_0 = array.array('b', (10+_ for _ in range(num_bytes)))
    dir0 = uctypes.addressof(buff_0)
    print('malloc',num_bytes,dir0,type(dir0))
    for address in range(dir0,dir0+num_bytes,4):
        write_memory(address,0)
    
    return dir0

#################################


URL_other='https://gerardomunoz.github.io'

# Connect to Wi-Fi
ssid = 'Ejemplo'
password = '12345678'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# Wait for connection
while not wlan.isconnected():
    pass

print('Connected to Wi-Fi')
print(wlan.ifconfig())

# HTML content to serve

htmls = ["""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Assembler Code Step Simulator</title>
    <style>
        textarea { width: 100%; }
        pre { background-color: #f0f0f0; padding: 10px; }
        table { width: 100%; }
        th, td { padding: 5px; text-align: left; }
    </style>
</head>
<body>
    <h1>Assembler Code Step Simulator</h1>
    <textarea id="codeInput" rows="15" cols="60">
backend 1
malloc R5,16
MOV R1,5
SETHI R2,1048944
LD R3,[R2+28]
SUBcc R1,R1,1
BzC -3
NOP
backend  0
NOP
NOP
backend 1
malloc R5,16
MOV R1,5
SETHI R2,3407872
ST [R2+172],31744
ST [R2+136],R1
ST [R2+128],R0
LD R3,[R2+148]
SUBcc R1,R1,1
BzC -2
NOP
backend  0
NOP
NOP
    </textarea>
    <br>
    <button onclick="step()"  id="btn_step">Step</button>
    <h2>Simulation Output</h2>
    <pre id="output"></pre>
    <h2>Register States</h2>
    <table>
        <thead>
            <tr><th>Register</th><th>Value</th></tr>
        </thead>
        <tbody id="registerTable">
        </tbody>
    </table>

""", """
  

<div id="memory-container">
    <!--input type="text" id="memory_address" placeholder="Memory Address"/-->
    <div id="backend-switch">
        <label class="switch">
            <input type="checkbox" id="backend-checkbox">
            <span class="slider"></span>
        </label>
        <span id="backend-text">Backend</span>
    </div>
</div> 
    
    <h2>Memory </h2>
<textarea id="memoryInput" rows="10" cols="60">  </textarea>


        
        <script>
        const sw_back = document.getElementById("backend-checkbox");
        //const txt_back = document.getElementById("backend-text");
        const btn_step = document.getElementById("btn_step");
        
        const instructions = [
            "ADD", "AND", "OR", "XOR", "SUB", "ANDN", "ORN", "XNOR", "ADDX", "UMUL", "SMUL", "SUBX", "UDIV", "SDIV",
            "ADDcc", "ANDcc", "ORcc", "XORcc", "SUBcc", "ANDNcc", "ORNcc", "XNORcc", "ADDXcc", "UMULcc", "SMULcc", "SUBXcc", "UDIVcc", "SDIVcc",
            "SLL", "SRL", "SRA",
            "LD", "ST",
            "BN", "BE", "BLE", "BL", "BLEU", "BCS", "BNEG", "BVS", "BA", "BNE", "BG", "BGE", "BGU", "BCC", "BPOS", "BVC",
            "CALL", "RETL", "JMPL",
            "SETHI",
            "NOP", "MOV", "CMP", "TST", "NOT", "NEG", "INC", "DEC", "CLR",
            "BnS", "BnC", "BzS", "BzC", "BcS", "BcC", "BvS", "BvC",
            "malloc", "backend",
        ];
""", """

        const registers = { R0: 0, R1: 0, R2: 0, R3: 0, R4: 0, R5: 0, R6: 0, R7: 0 };
        let memory = registers//{R0: 0, R1: 0, R2: 0, R3: 0, R4: 0, R5: 0, R6: 0, R7: 0};

        let parsed = [];
        let instructionPointer = 0;

        function tokenize(code) {
            return code
                .replace(/,\s*/g, ',') // Remove extra spaces after commas
                .split(/[\s,]+/) // Split by any whitespace
                .filter(token => token.length > 0); // Remove empty tokens
                
        }

        function parse(tokens) {
            const parsed = [];
            let i = 0;

            while (i < tokens.length) {
                const token = tokens[i];

                if (instructions.includes(token)) {
                    const instruction = { op: token };
                    i++;

                    const args = [];
                    while (i < tokens.length && !instructions.includes(tokens[i]) && tokens[i] !== 'NOP') {
                        let arg = tokens[i].replace(/,$/, '');

                        if (arg.startsWith('[') && arg.endsWith(']')) {
                            arg = arg.slice(1, -1); // Remove brackets
                            if (arg.includes('+')) {
                                args.push(`[${arg}]`);
                            } else {
                                args.push(arg);
                            }
                        } else {
                            args.push(arg);
                        }

                        i++;
                    }
                    instruction.args = args;
                    parsed.push(instruction);
                } else {
                    i++;
                }
            }
            return parsed;
        }

""", """

       function sendJson(jsonData) {
            btn_step.style.color = "red"
            btn_step.textContent  = "Wait";
            //btn_step.onclick = "";
            console.log('sendJson')
            const queryString = new URLSearchParams(jsonData).toString();

            fetch(`/api?${queryString}`)
                .then(response => response.json())  // Expecting a JSON response
                .then(data => {
                    console.log('sendJson',data);
                    btn_step.style.color = "black";
                    btn_step.textContent  = "Step";
                    //btn_step.onclick = "step()";
                    
                   
                    for (const [key, value] of Object.entries(data)) {
                        console.log(`Key: ${key}, Value: ${value}`);
                        memory[key]=parseInt(value)
                    }
                 })
                .catch(error => console.error('sendJson Error:', error));
        }
        
        function read_memory(address,rd){
            if (address % 4 !== 0) {
                throw new Error(`The address ${address} is not divisible by 4.`);
            }
            if (sw_back.checked) {
                //console.log('malloc..2')
                const jsonData = {
                    read_memory: [address,rd],
                    //rd:rd
                    //key2b: "value2b",
                    //key3c: "value3c"
                };

                sendJson(jsonData)
                //...
                //...
            } else{
                if (!(memory.hasOwnProperty(address))){
                            memory[address] = parseInt(prompt("Value of memory "+address, "0")); 
                        }
                return memory[address];
            }
        }
""", """

        function write_memory(address,data){
            if (address % 4 !== 0) {
                throw new Error('The address '+address+'     is not divisible by 4.     ');
            }
            if (sw_back.checked) {
                //console.log('malloc..2')
                const jsonData = {
                    write_memory: [address,data],
                    //key2b: "value2b",
                    //key3c: "value3c"
                };

                sendJson(jsonData)
                //...
            } else{
                memory[address] = data; 
            }
        }
""", """

        function malloc(num_bytes,rd){
            if (num_bytes % 4 !== 0) {
                throw new Error(`The number ${num_bytes} is not divisible by 4.`);
            }
            console.log('malloc..1a')
            if (sw_back.checked) {
                
                const jsonData = {
                    malloc: [num_bytes,rd],
                    //rd,rd
                    //key2b: "value2b",
                    //key3c: "value3c"
                };
                console.log('malloc..2',jsonData)
                sendJson(jsonData)
            } else{
                address=parseInt(prompt("Address of memory ", "0"));
                for (var i = 0; i < num_bytes; i=i+4) {
                    memory[address+i] = 0; 
                }
            }
        }
        
""", """

function executeInstruction(instruction) {
            const args = instruction.args.map(arg => {
                if (arg.startsWith('[')) {
                    const parts = arg.slice(1, -1).split('+');
                    const regValue = registers[parts[0]];
                    const offset = parts[1] ? parseInt(parts[1], 10) : 0;
                    return regValue + offset;
                //} else if (registers.hasOwnProperty(arg)) {
                } else if (arg.startsWith('R')) {    
                    return registers[arg];
                } else {
                    return parseInt(arg, 10);
                }
            });

            switch (instruction.op) {
                case 'MOV':
                    
                    registers[instruction.args[0]] = args[1];
                    break;
                case 'LD':
                    //registers[instruction.args[0]] = read_memory(args[1]);
                    read_memory(args[1],instruction.args[0]);
                    break;
                case 'ST':
                    write_memory(args[0], args[1]);
                    break;
                case 'ADD':
                    registers[instruction.args[0]] = args[1] + args[2];
                    break;
                case 'SUB':
                    registers[instruction.args[0]] = no_flags([1] - args[2]);
                    break;
                case 'SUBcc':
                    registers[instruction.args[0]] = flags(args[1] - args[2]);
                    break;
                case 'SUBcc':
                    registers[instruction.args[0]] = flags(args[1] - args[2]);
                    break;
                case 'SMUL':
                    registers[instruction.args[0]] = args[1] * args[2];
                    break;
                case 'INC':
                    registers[instruction.args[0]] += 1;
                    break;
                case 'DEC':
                    registers[instruction.args[0]] -= 1;
                    break;
                case 'SLL':
                    registers[instruction.args[0]] = args[1] << args[2];
                    break;
                case 'SETHI':
                    registers[instruction.args[0]] = args[1] << 10;
                    break;
                case 'CLR':
                    registers[instruction.args[0]] = 0;
                    break;
                case 'CMP':
                    registers['FLAG'] = args[0] - args[1];
                    break;
                case 'BzS':
                    if (registers['FLAG'] === 0) {
                        return args[0];
                    }
                    break;
                case 'BzC':
                    if (registers['FLAG'] !== 0) {
                        return args[0];
                    }
                    break;
                case 'BA':
                    return args[0];
                    break;
                case 'NOP':
                    break;
                case 'malloc': //malloc Rd,  Cte
                        // malloc: Allocates a block of memory on the heap at runtime.
                        // Rd: Register that stores the address of the beginning of the allocated block.
                        // Cte: The number of bytes to allocate, which must be a multiple of 4 to ensure proper 4 bytes memory alignment.
                    console.log('malloc')
                    malloc(args[1],instruction.args[0])
                    break;
                case 'backend': //backend 0; backend 1
                    console.log('backend',sw_back.checked)
                    sw_back.checked=Boolean(args[0])
                    console.log('backend',sw_back.checked)
                    break;
                default:
                    console.log(`Unknown instruction: ${instruction.op}`);
            }
            return null;
        }
""", """
        function no_flags(resultado){
            if (resultado >= 4294967296){ //2**32
                return resultado % 4294967296;
            }else if (registers['resultado']<0 && registers['resultado']>(-2147483648)){
                registers['resultado']= (registers['resultado'] % 4294967296) + 4294967296;
            }else if(registers['resultado']<=(-2147483648)){
                registers['resultado']= (registers['resultado'] % 4294967296) + 4294967296;
            }
            return args[0];
        }
        function flags(resultado){// los numeros de registers['resultado'] van entre o y (2**32) -1, es obligacion de cada uno revisar que la operacion se cumple bien cuando los valores de los registros estan con signo
            if (resultado >= 4294967296){ //2**32
                registers['c']=1;
                registers['n']=0;
                registers['z']=0;
                registers['v']=1;
                return resultado % 4294967296;
            } else if (registers['resultado']>= 2147483648 && registers['resultado']< 4294967296){
                registers['c']=0;
                registers['n']=1;
                registers['z']=0;
                registers['v']=1;
            }else if (registers['resultado']<2147483648 && registers['resultado']>0){
                registers['c']=0;
                registers['v']=0;
                registers['n']=0;
                registers['z']=0;
            }else if (registers['resultado']==0){
                registers['z']=1;
                registers['c']=0;
                registers['n']=0;
                registers['v']=0; 
            }else if (registers['resultado']<0 && registers['resultado']>(-2147483648)){
                registers['c']=1;
                registers['n']=1;
                registers['z']=0;
                registers['v']=0;
                registers['resultado']= (registers['resultado'] % 4294967296) + 4294967296;
            }else if(registers['resultado']<=(-2147483648)){
                registers['c']=1;
                registers['n']=0;
                registers['z']=0;
                registers['v']=1;
                registers['resultado']= (registers['resultado'] % 4294967296) + 4294967296;
            }
            return resultado;
        }
        
        function step() {
            if (instructionPointer === 0) {
                const code = document.getElementById('codeInput').value;
                const tokens = tokenize(code);
                console.log(tokens)
                parsed = parse(tokens);
                console.log(parsed)
                
                const memoryInput = document.getElementById('memoryInput').value;
                for (let i = 100; i < 116; i=i+4) {
                    memory[i] = i+1000;
                   }
                //memory = memoryInput.split(',').map(Number); // Initialize memory from textarea
            }

            if (instructionPointer < parsed.length) {
                const output = 'Executing: '+parsed[instructionPointer].op + parsed[instructionPointer].args.join(", ")+'\\n';
                document.getElementById('output').textContent += output; 

                const jump = executeInstruction(parsed[instructionPointer]);
                if (jump !== null) {
                    instructionPointer += jump;
                } else {
                    instructionPointer++;
                }

                updateRegisterTable();
                updateMemoryTextarea();
            } else {
                document.getElementById('output').textContent += "Simulation complete.\\n";
            }
        }
""", """

        function updateRegisterTable() {
            const table = document.getElementById('registerTable');
            table.innerHTML = '';
            for (const [reg, value] of Object.entries(registers)) {
                table.innerHTML += `<tr><td>${reg}</td><td>${value}</td></tr>`;
            }
        }

        function updateMemoryTextarea() {
        console.log('updateMemoryTextarea',memory)
            document.getElementById('memoryInput').value = JSON.stringify(memory, null, 4);
        }
//Powered by ChatGPT
        </script>
    </body>
</html>
"""]
for i in range(len(htmls)):
    html = htmls[i].replace('\r\n', '\n')  # Primero aseguramos que todo sea \n
    htmls[i] = html.replace('\n', '\r\n')  # Luego los convertimos todos a \r\n

def str2tuple(txt):
    print('str2tuple',txt)
    return txt.strip("()[}").replace('%2C',',').split(",")
                  

# Function to handle incoming requests
def handle_request(client):
    request = client.recv(1024)
    request_str = request.decode('utf-8')
    
    print('Received request:')
    print(request_str)

    # Serve the HTML page
    if 'GET / ' in request_str or 'GET /api' not in request_str:
        client.send('HTTP/1.1 200 OK\r\n')
        client.send('Content-Type: text/html\r\n')
        client.send('Connection: close\r\n\r\n')
        for html in htmls:
            client.send(html)
            time.sleep_ms(100)
        client.close()
        
      
    
    # Handle the API request
    elif 'GET /api' in request_str:
        match = ure.search(r'GET /api\?([^\s]+) HTTP', request_str)
        response_dir={}
        if match:
            query_string = match.group(1)
            params = query_string.split('&')
            json_data = {}
            for param in params:
                key, value = param.split('=')
                json_data[key] = value
            
            print("Received JSON data:")
            dat_r=json.dumps(json_data)
            print(json_data)  # Pretty print the JSON data
            for key,val in json_data.items():
                print('dic',key,val)
                if key=='malloc':
                    numb,rd = str2tuple(val)
                    numb=int(numb)
                    address=malloc(numb,rd)
                    for addr_i in range(address,address+numb,4):
                        response_dir[addr_i]=0
                    response_dir[rd]=address
                elif key=='write_memory':
                    
                    #cleaned_string = val.strip("()")
                    #addr,dat = cleaned_string.split(",")
                    addr,dat = str2tuple(val)
                    addr=int(addr)
                    dat=int(dat)
                    write_memory(addr,dat)
                    response_dir[addr]=dat
                elif key=='read_memory':
                    addr,rd = str2tuple(val)
                    addr=int(addr)
                    dat=read_memory(addr,rd)
                    response_dir[addr]=dat
                    response_dir[rd]=dat
#     def malloc(num_bytes):
#     print('malloc',num_bytes)
# 
# 
# def write_memory(address,data):
#     print( 'write_memory',address,data)
#     
#     
# read_memory(address):
#     print('read_memory',address)
        response_json = json.dumps(response_dir)
        print(response_json)
        client.send('HTTP/1.1 200 OK\r\n')
        #client.send('Content-Type: text/plain\r\n')
        #client.send('Connection: close\r\n\r\n')
        #client.send('Request received and processed\r\n')
        client.send('Content-Type: application/json\r\n')
        client.send('Connection: close\r\n\r\n')
        client.send(response_json)  # Send JSON response
    
    client.close()

# Start the server
def start_server():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    server_socket = socket.socket()
    server_socket.bind(addr)
    server_socket.listen(1)
    
    print('Server listening on', addr)
    
    while True:
        client, addr = server_socket.accept()
        print('Client connected from', addr)
        handle_request(client)

# Start the web server
start_server()
#Powered by ChatGPT
