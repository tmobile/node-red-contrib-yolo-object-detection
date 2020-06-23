const { spawn } = require('child_process')

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
            node.debug('Current dir is: ' + __dirname)
            python = spawn('python3', ['4_Serve/Serve.py'])

            globalContext.set('yoloserver', python)
            node.log('Loaded Yoloserver')

            python.stdout.on('data', (data) => {
                node.debug(data.toString())
            })

            python.stderr.on('data', (data) => {
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
        // TODO
        // 22 Jun 13:25:30 - [debug] [yolo-object-detection:303f8140.0f1666] Init Node count is: 3
        // 22 Jun 13:25:30 - [info] Started flows
        // (node:24064) MaxListenersExceededWarning: Possible EventEmitter memory leak detected. 11 data listeners added to [Socket]. Use emitter.setMaxListeners() to increase limit
        // (Use `node --trace-warnings ...` to show where the warning was created)
        // (node:24064) MaxListenersExceededWarning: Possible EventEmitter memory leak detected. 11 data listeners added to [Socket]. Use emitter.setMaxListeners() to increase limit
        // (node:24064) MaxListenersExceededWarning: Possible EventEmitter memory leak detected. 11 close listeners added to [ChildProcess]. Use emitter.setMaxListeners() to increase limit
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
                nodeCount--
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
