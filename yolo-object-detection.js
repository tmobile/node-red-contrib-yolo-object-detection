const { spawn } = require('child_process')

module.exports = (RED) => {
    let python = null
    // This is a crappy hack but whatever
    let nodeCount = 0

    let serverStatus = { fill: 'yellow', shape: 'dot', text: 'connecting' }

    spawn('source', ['model-server/env/bin/activate'])

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
            node.debug('Current dir is: ' + __dirname)
            python = spawn('env/bin/python3', ['python-scripts/4_Serve/ServeAll.py'], {'cwd': __dirname})

            globalContext.set('yoloserver', python)
            node.log('Loaded Yoloserver')

            python.stdout.on('data', (data) => {
                console.log(data.toString())
                node.debug(data.toString())
            })

            python.stderr.on('data', (data) => {
                console.log(data.toString())
                if (data.toString().includes('Running on http://0.0.0.0')) {
                    serverStatus = { fill: 'green', shape: 'dot', text: 'connected' }
                    node.status(serverStatus)
                } else if (node.status.text !== 'connected') {
                    serverStatus = { fill: 'yellow', shape: 'dot', text: 'connecting' }
                    node.status(serverStatus)
                }
                node.debug(data.toString())
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
    }

    function YoloObjectDetection (config) {
        RED.nodes.createNode(this, config)
        this.debug('NODE DEPLOYED AND STARTED')
        initObjectDetectorYolo(this)
    }
    RED.nodes.registerType('yolo-object-detection', YoloObjectDetection)
}
