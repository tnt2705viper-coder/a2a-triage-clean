from flask import Flask, render_template, request

app = Flask(__name__)

def classify(pulse, systolic, diastolic, spo2, meds):

    warning = None

    # Kiểm tra thiếu sinh hiệu
    if not pulse or not systolic or not diastolic or not spo2:
        warning = "⚠️ Vui lòng bổ sung đầy đủ sinh hiệu"

    # Ép kiểu nếu có giá trị
    pulse = int(pulse) if pulse else None
    systolic = int(systolic) if systolic else None
    diastolic = int(diastolic) if diastolic else None
    spo2 = int(spo2) if spo2 else None

    # =========================
    # ====== ƯU TIÊN ĐỎ =======
    # =========================

    # Thuốc vận mạch -> ĐỎ (KHÔNG cần đủ sinh hiệu)
    if "dobutamin" in meds or "noradrenalin" in meds:
        return combine_result(
            "🔴 ĐỎ - Đang dùng thuốc vận mạch\n➡ Xếp bệnh nhân vào PHÒNG CẤP CỨU",
            "red",
            warning
        )

    # HA thấp nguy hiểm
    if systolic is not None and diastolic is not None:
        if systolic < 90 or diastolic < 60:
            return combine_result(
                "🔴 ĐỎ - Huyết áp nguy hiểm\n➡ Xếp bệnh nhân vào PHÒNG CẤP CỨU",
                "red",
                warning
            )

    # SpO2 nguy hiểm
    if spo2 is not None:
        if spo2 < 90:
            return combine_result(
                "🔴 ĐỎ - SpO2 nguy hiểm\n➡ Xếp bệnh nhân vào PHÒNG CẤP CỨU",
                "red",
                warning
            )

    # Mạch nguy hiểm
    if pulse is not None:
        if pulse < 50 or pulse > 160:
            return combine_result(
                "🔴 ĐỎ - Mạch nguy hiểm\n➡ Xếp bệnh nhân vào PHÒNG CẤP CỨU",
                "red",
                warning
            )

    # =========================
    # ====== ƯU TIÊN VÀNG =====
    # =========================

    # Nếu có checkbox (ngoài vận mạch)
    if len(meds) > 0:
        return combine_result(
            "🟡 VÀNG - Có sử dụng thuốc nguy cơ\n➡ Xếp bệnh nhân vào PHÒNG THEO DÕI (3,4,10,11)",
            "yellow",
            warning
        )

    # HA cao
    if systolic is not None and diastolic is not None:
        if systolic > 180 or diastolic > 100:
            return combine_result(
                "🟡 VÀNG - Huyết áp cao\n➡ Xếp bệnh nhân vào PHÒNG THEO DÕI (3,4,10,11)",
                "yellow",
                warning
            )

    # SpO2 giảm
    if spo2 is not None:
        if spo2 < 95:
            return combine_result(
                "🟡 VÀNG - SpO2 giảm\n➡ Xếp bệnh nhân vào PHÒNG THEO DÕI (3,4,10,11)",
                "yellow",
                warning
            )

    # Mạch nhanh
    if pulse is not None:
        if pulse > 110:
            return combine_result(
                "🟡 VÀNG - Mạch nhanh\n➡ Xếp bệnh nhân vào PHÒNG THEO DÕI (3,4,10,11)",
                "yellow",
                warning
            )

    # =========================
    # ========= XANH ==========
    # =========================

    # Chỉ xanh khi đủ sinh hiệu và không có thuốc
    if not warning and len(meds) == 0:
        return (
            "🟢 XANH - Sinh hiệu ổn định\n➡ Xếp bệnh nhân vào PHÒNG THƯỜNG",
            "green"
        )

    # Nếu thiếu sinh hiệu mà không đủ dữ kiện phân loại
    return combine_result(
        "⚠️ Chưa đủ dữ kiện phân loại chính xác",
        "normal",
        warning
    )


def combine_result(main_text, level, warning):
    if warning:
        full_text = warning + "\n\n" + main_text
        return full_text, level
    return main_text, level


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    level = None

    if request.method == "POST":
        pulse = request.form.get("pulse")
        systolic = request.form.get("systolic")
        diastolic = request.form.get("diastolic")
        spo2 = request.form.get("spo2")
        meds = request.form.getlist("meds")

        result, level = classify(pulse, systolic, diastolic, spo2, meds)

    return render_template("index.html", result=result, level=level)


if __name__ == "__main__":
    app.run(debug=True)