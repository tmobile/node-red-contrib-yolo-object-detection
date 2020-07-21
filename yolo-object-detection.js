const { spawn } = require('child_process')
const http = require('http')

module.exports = (RED) => {
    let python = null
    // This is a crappy hack but whatever
    let nodeCount = 0

    let serverStatus = { fill: 'yellow', shape: 'dot', text: 'connecting' }

    // Initialize the TensorFlow.js library and store it in the Global
    // context to make sure we are running only one instance
    const initObjectDetectorYolo = (node) => {
        node.status(serverStatus)
        const globalContext = node.context().global

        nodeCount = globalContext.get('object-detector-node-count')
        nodeCount = nodeCount || 0
        nodeCount++

        node.debug('Init Node count is: ' + nodeCount)

        globalContext.set('object-detector-node-count', nodeCount)

        if (!python) {
            python = globalContext.get('yoloserver')
        }

        if (!python || python.killed) {
            node.debug('Starting python server process')
            node.debug(`Current dir is: ${__dirname} `)
            python = spawn('env/bin/python3', ['model-server/ServeAll.py'], { cwd: __dirname })

            globalContext.set('yoloserver', python)
            node.log('Loaded Yoloserver')

            python.stdout.on('data', (data) => {
                if (data.toString().includes('MODELSERVER: Model initialized')) {
                    serverStatus = { fill: 'green', shape: 'dot', text: 'connected' }
                    node.status(serverStatus)
                }
                node.debug(data.toString())
            })

            python.stderr.on('data', (data) => {
                if (data.toString().includes('MODELSERVER: Model initialized')) {
                    serverStatus = { fill: 'green', shape: 'dot', text: 'connected' }
                    node.status(serverStatus)
                }
                console.log(data.toString())
            })

            python.on('close', (code, signal) => {
                serverStatus = { fill: 'red', shape: 'ring', text: 'disconnected' }
                node.status(serverStatus)
                node.debug(
                    `Python server process terminated due to receipt of signal ${signal}`)
            })
        }

        node.on('close', (removed, done) => {
            nodeCount = globalContext.get('object-detector-node-count')
            node.debug('Pre-dec close Node count is: ' + nodeCount)
            nodeCount--
            globalContext.set('object-detector-node-count', nodeCount)
            if (removed && nodeCount <= 0) {
                // Happens when the node is removed and the flow is deployed or restarted
                node.debug('Node removed, and is the last node, so cleaning up server')
                python.kill()
            } else if (removed) {
                node.debug('Node removed, but not the last node')
            } else {
                // Happens when the node is in the flow, and the flow is deployed or restarted
                node.debug('Node redeployed or restarted')
            }
            done()
        })

        node.on('input', function (msg, send, done) {
            const options = {
                hostname: 'localhost',
                path: '/',
                port: '8888',
                method: 'POST',
                headers: {
                }
            }

            let requestBody = null
            try {
                node.debug('Forwarding raw image payload')
                requestBody = msg.payload
                options.headers['Content-Length'] = Buffer.byteLength(requestBody)
            } catch (e) {
                node.debug('Forwarding JSON payload')
                options.headers['Content-Type'] = 'application/json'
                requestBody = JSON.stringify(msg.payload)
                options.headers['Content-Length'] = requestBody.length
            }

            let data = ''

            http.request(options, res => {
                data = ''
                res.on('data', d => {
                    data += d
                })
                res.on('end', () => {
                    if (res.statusCode === 200) {
                        node.debug(data)
                        send = send || function () { node.send.apply(node, arguments) }
                        msg.payload = JSON.parse(data)
                        send(msg)
                    } else {
                        node.error(`Error connecting to model server, response code was ${res.statusCode} and message was ${res.statusMessage}`)
                        serverStatus = { fill: 'red', shape: 'ring', text: 'disconnected' }
                        node.status(serverStatus)
                    }
                })
            }).on('error', () => {
                node.error('Error connecting to model server')
                serverStatus = { fill: 'red', shape: 'ring', text: 'disconnected' }
                node.status(serverStatus)
            }).end(requestBody)

            // This call is wrapped in a check that 'done' exists
            // so the node will work in earlier versions of Node-RED (<1.0)
            if (done) {
                done()
            }
        })
    }

    function YoloObjectDetection (config) {
        RED.nodes.createNode(this, config)
        this.debug('NODE DEPLOYED AND STARTED')
        initObjectDetectorYolo(this)
    }
    RED.nodes.registerType('yolo-object-detection', YoloObjectDetection)
}
