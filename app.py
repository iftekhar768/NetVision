from flask import Flask, render_template, request, redirect
from config import Config
from models.device import db, Device
from monitoring.ping_monitor import check_device
from sqlalchemy import or_
from monitoring.scheduler import scheduler
from monitoring.ping_monitor import scan_all_devices

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

def scheduled_scan():
    with app.app_context():
        scan_all_devices()


@app.route("/")
def home():

    total = Device.query.count()

    online = Device.query.filter_by(status="Online").count()

    offline = Device.query.filter_by(status="Offline").count()

    return render_template(
        "dashboard.html",
        total=total,
        online=online,
        offline=offline
    )

@app.route("/devices")
def devices():

    search = request.args.get("search")

    if search:
        all_devices = Device.query.filter(
            or_(
                Device.name.ilike(f"%{search}%"),
                Device.ip_address.ilike(f"%{search}%")
            )
        ).all()
    else:
        all_devices = Device.query.all()

    return render_template(
        "devices.html",
        devices=all_devices
    )

@app.route("/add-device", methods=["GET", "POST"])
def add_device():

    if request.method == "POST":

        device = Device(
            name=request.form["name"],
            ip_address=request.form["ip_address"],
            location=request.form["location"]
        )

        db.session.add(device)
        db.session.commit()

        return redirect("/devices")

    return render_template("add_device.html")

@app.route("/scan")
def scan():

    scan_all_devices()

    return redirect("/devices")
def scan_all_devices():
    devices = Device.query.all()

    for device in devices:
        old_status = device.status
        new_status = check_device(device.ip_address)

        device.status = new_status

        print(f"{device.name}: {old_status} -> {new_status}")

    db.session.commit()

    print("Network Scan Completed")

@app.route("/edit-device/<int:id>", methods=["GET", "POST"])
def edit_device(id):

    device = Device.query.get_or_404(id)

    if request.method == "POST":

        device.name = request.form["name"]
        device.ip_address = request.form["ip_address"]
        device.location = request.form["location"]

        db.session.commit()

        return redirect("/devices")

    return render_template(
        "edit_device.html",
        device=device
    )

@app.route("/delete-device/<int:id>")
def delete_device(id):

    device = Device.query.get_or_404(id)

    db.session.delete(device)
    db.session.commit()

    return redirect("/devices")

with app.app_context():
    db.create_all()
    scheduler.start()

scheduler.add_job(
    scheduled_scan,
    "interval",
    seconds=30
)

if not scheduler.running:
    scheduler.start()

if __name__ == "__main__":
    app.run(debug=True)