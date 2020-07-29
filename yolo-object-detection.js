const decompress = require('decompress-zip')
const fs = require('fs')
const http = require('http')
const multer = require('multer')
const path = require('path')
const { spawn } = require('child_process')

module.exports = (RED) => {
    let python = null
    // This is a crappy hack but whatever
    let nodeCount = 0

    let serverStatus = { fill: 'yellow', shape: 'dot', text: 'connecting' }

    let modelsDir = RED.settings.modelsDir || process.env.HOME + "/models"
    // Create models directory if not present.
    if (!fs.existsSync(modelsDir)){
        fs.mkdirSync(modelsDir);
    }

    // Initialize the TensorFlow.js library and store it in the Global
    // context to make sure we are running only one instance
    const initObjectDetectorYolo = (node) => {
        node.status(serverStatus)
        node.debug(`modelsDir: ${modelsDir}`)
        node.debug(`modelName: ${node.modelName}`)
        node.debug(`modelPath: ${node.modelPath}`)
        const globalContext = node.context().global

        nodeCount = globalContext.get('object-detector-node-count')
        nodeCount = nodeCount || 0
        nodeCount++

        node.debug('Init Node count is: ' + nodeCount)

        globalContext.set('object-detector-node-count', nodeCount)

        if (!python) {
            python = globalContext.get('yoloserver')
        }

        // Kill child process if model path changed to load new model.
        node.debug(`lastModelPath: ${globalContext.get('lastModelPath')}`)
        if (python && node.modelPath !== globalContext.get('lastModelPath')) {
            node.debug(`New model, killing current child process`)
            python.kill()
            python = null
        }
        // Save last model path for comparison to restart when changed.
        globalContext.set('lastModelPath', node.modelPath)

        if (!python || python.killed) {
            node.debug('Starting python server process')
            node.debug(`Current dir is: ${__dirname} `)
            process.env.MODEL_PATH = node.modelPath
            node.debug(`env MODEL_PATH: ${process.env.MODEL_PATH}`)
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
            if (msg.payload['video-frame'] === true) {
                requestBody = JSON.stringify(msg.payload)
                options.headers['Content-Type'] = 'application/json'
                options.headers['Content-Length'] = requestBody.length
                node.debug('Forwarding JSON payload')
            } else {
                requestBody = msg.payload
                options.headers['Content-Length'] = Buffer.byteLength(requestBody)
                node.debug('Forwarding raw image payload')
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
        this.modelName = config.modelName || "yolov3"
        this.modelPath = path.join(modelsDir, this.modelName)
        initObjectDetectorYolo(this)
    }
    RED.nodes.registerType('yolo-object-detection', YoloObjectDetection)

    // Create admin endpoint to list currently available models.
    RED.httpAdmin.get("/models", function (req, res) {
        let models = []
        fs.readdirSync(modelsDir).forEach(fileName => {
            let filePath = path.join(modelsDir , fileName)
            let stat = fs.statSync(filePath)
            if (stat && stat.isDirectory()) {
                models.push(fileName)
            }
        })
        res.json(models)
    })

    // Create admin endpoint to upload new models.
    // Use multer middleware to handle multipart form file data upload.
    // Write to disk for large model files.
    const storage = multer.diskStorage({
        destination: function (req, file, cb) {
            cb(null, modelsDir)
        },
        filename: function (req, file, cb) {
            cb(null, file.originalname)
        }
    })
    const upload = multer({storage: storage})
    RED.httpAdmin.post("/models/upload", upload.single('file'), function (req, res, next) {
        const file = req.file
        if (!file) {
            const error = new Error('Problems uploading file')
            error.httpStatusCode = 400
            return next(error)
        }
        // Extract the zip file.
        console.log(`Unzipping file ${file.path}`)
        const unzipper = new decompress(file.path)
        unzipper.on("extract", function () {
            console.log("Unzip extraction complete.")
            // Remove zip file.
            try {
                fs.unlinkSync(file.path)
            } catch (err) {
                console.error(err)
            }
        })
        unzipper.extract({ path: modelsDir })
        // res.status(204).end()
        res.send(file)
    })
}
