from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, time
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)
CORS(app)

# Firebase init
cred = credentials.Certificate("serviceAccountKey.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://easy-22b8-default-rtdb.firebaseio.com/'
    })



@app.route('/', methods=['GET'])
def index():
    return "Flask middleware running", 200


@app.route('/', methods=['POST'])
def receive_data():
    json_data = request.get_json(silent=True)

    device_id = None
    lat = None
    lon = None

    if json_data:
        device_id = json_data.get("device_id")
        location = json_data.get("location", {})
        coords = location.get("coords", {})
        lat = coords.get("latitude")
        lon = coords.get("longitude")

    if device_id and lat and lon:
        db.reference(f"buses/{device_id}/location").set({
            "lat": float(lat),
            "lng": float(lon),
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        return "Location updated", 200

    return "Missing id, lat, or lon", 400



ENTRY_START = time(7, 0)
ENTRY_END = time(9, 30)

EXIT_START = time(16, 30)
EXIT_END = time(19, 0)


@app.route('/scan-attendance', methods=['POST'])
def scan_attendance():

    data = request.json
    roll = data.get("roll")
    bus_id = data.get("busId")
    token = data.get("token")
    qr_type = data.get("type")   # entry or exit

    if not roll or not bus_id or not token or not qr_type:
        return jsonify({"status":"error","msg":"Missing data"}),400

    now = datetime.now().time()

    if qr_type == "entry":
        if not (ENTRY_START <= now <= ENTRY_END):
            return jsonify({
                "status":"error",
                "msg":"Entry allowed only 7:00–9:30 AM"
            }),403

    if qr_type == "exit":
        if not (EXIT_START <= now <= EXIT_END):
            return jsonify({
                "status":"error",
                "msg":"Exit allowed only 4:30–7:00 PM"
            }),403

    token_data = db.reference(f"busTokens/bus{bus_id}/{qr_type}").get()

    if not token_data or token_data.get("token") != token:
        return jsonify({"status":"error","msg":"Invalid or expired QR"}),403

    ref = db.reference(f"attendance/bus{bus_id}/{roll}")
    existing = ref.get() or {}

    if qr_type == "entry" and existing.get("entryTime"):
        return jsonify({"status":"error","msg":"Entry already marked"}),403

    if qr_type == "exit" and existing.get("exitTime"):
        return jsonify({"status":"error","msg":"Exit already marked"}),403

    ref.update({
        f"{qr_type}Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    print(f"{roll} {qr_type} attendance saved")

    return jsonify({
        "status":"success",
        "mode":qr_type
    })


if __name__ == '__main__':
    print("🚀 Flask running on port 5055")
    app.run(host="0.0.0.0", port=5055, debug=True)