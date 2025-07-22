# Robot Hackathon Edge Controller

The Edge Controller is a python Server publishing a REST-API to control the robot.

The Gopigo will turn on the left eye led to signal the running api.

## Quick Start

```shell
# Install dependencies
pip3 install -r requirements.txt

# Start the server
python3 ./edgehub.py
```

The GoPiGo will turn on the left eye LED when the API is running at `http://<robot-ip>:5000`

##  API Endpoints

### Status
* `GET /` - Health check
* `GET /distance` - Distance sensor reading (mm)
* `GET /power` - Battery voltage
###  Movement
* `POST /forward/<cm>` - Move forward
* `POST /backward/<cm>` - Move backward  
* `POST /left/<degrees>` - Turn left
* `POST /right/<degrees>` - Turn right
* `POST /servo/<degrees>` - Rotate servo

### Camera & Servo
* `GET /camera` - Get base64-encoded JPEG image
* `GET /camera.jpg` - Get JPEG image

#### NOTE
Camera returns HTTP 423 if robot is moving. Movement operations are thread-safe and execute one at a time.


## Examples

```shell
# Move forward 20cm
curl -X POST http://192.168.1.100:5000/forward/20

# Get camera image
curl http://192.168.1.100:5000/camera > image.b64

# Check distance
curl http://192.168.1.100:5000/distance
```

## Production Deployment

```shell
cd /opt/
git clone --depth 1 \
    --single-branch \
    --branch v2.0.0 \
    https://github.com/cloud-native-robotz-hackathon/edge-controller.git

cd edge-controller
cp -v edge-controller.service /etc/systemd/system/
systemctl enable --now edge-controller
```

## Troubleshooting

* **Camera issues**: Check `/dev/video0` exists and permissions
* **Robot not responding**: Verify GoPiGo3 libraries and battery level
* **Service logs**: `sudo journalctl -u edgehub.service`
