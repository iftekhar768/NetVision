from flask import Flask, render_template, request, redirect
from config import Config
from models.device import db, Device
from monitoring.ping_monitor import check_device

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


@app.route("/")
def home():
    return render_template("dashboard.html")


@app.route("/devices")
def devices():
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

    devices = Device.query.all()

    for device in devices:

        device.status = check_device(device.ip_address)

    db.session.commit()

    return redirect("/devices")

with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)