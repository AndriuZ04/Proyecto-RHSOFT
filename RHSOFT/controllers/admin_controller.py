from flask import render_template

def dashboard_admin():

    return render_template(
        "admin/dashboard.html"
    )