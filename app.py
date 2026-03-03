from flask import Flask, render_template, request

app = Flask(__name__)

def combine_result(main_text, level, warning):
    if warning:
        return warning + "\n\n" + main_text, level
    return main_text, level


def classify(pulse, systolic, diastolic, spo2,
             meds,
             chest_pain, dyspnea,
             gcs_status,
             stemi,
             oxygen_type):

    warning = None

    if not pulse or not systolic or not diastolic or not spo2:
        warning = "⚠️ Vui lòng bổ sung đầy đủ sinh hiệu"

    # Ép kiểu
    pulse = int(pulse) if pulse else None
    systolic = int(systolic) if systolic else None
    diastolic = int(diastolic) if diastolic else None
    spo2 = int(spo2) if spo2 else None

    # =====================================
    # 🔴 ƯU TIÊN ĐỎ – LÂM SÀNG TUYỆT ĐỐI
    # =====================================

    # STEMI
    if stemi:
        return combine_result(
            "🔴 ĐỎ - ECG có STEMI\n➡ PHÒNG CẤP CỨU / KÍCH HOẠT CAN THIỆP",
            "red",
            warning
        )

    # GCS < 15
    if gcs_status == "lt15":
        return combine_result(
            "🔴 ĐỎ - Rối loạn tri giác (GCS < 15)\n➡ PHÒNG CẤP CỨU",
            "red",
            warning
        )

    # Oxy mask trở lên
    if oxygen_type == "mask":
        return combine_result(
            "🔴 ĐỎ - Cần oxy mask trở lên\n➡ PHÒNG CẤP CỨU",
            "red",
            warning
        )

    # Thuốc vận mạch
    if "dobutamin" in meds or "noradrenalin" in meds:
        return combine_result(
            "🔴 ĐỎ - Đang dùng thuốc vận mạch\n➡ PHÒNG CẤP CỨU",
            "red",
            warning
        )

    # HA thấp
    if systolic is not None and diastolic is not None:
        if systolic < 90 or diastolic < 60:
            return combine_result(
                "🔴 ĐỎ - Huyết áp nguy hiểm\n➡ PHÒNG CẤP CỨU",
                "red",
                warning
            )

    # SpO2 rất thấp
    if spo2 is not None and spo2 < 90:
        return combine_result(
            "🔴 ĐỎ - SpO2 < 90%\n➡ PHÒNG CẤP CỨU",
            "red",
            warning
        )

    # Mạch cực đoan
    if pulse is not None and (pulse < 50 or pulse > 160):
        return combine_result(
            "🔴 ĐỎ - Tần số tim nguy hiểm (theo ECG)\n➡ PHÒNG CẤP CỨU",
            "red",
            warning
        )

    # =====================================
    # 🟡 ƯU TIÊN VÀNG
    # =====================================

    # Đau ngực / khó thở
    if chest_pain or dyspnea:
        return combine_result(
            "🟡 VÀNG - Có triệu chứng nguy cơ (đau ngực / khó thở)\n➡ PHÒNG THEO DÕI (GẦN CẤP CỨU: P3,4,10,11)",
            "yellow",
            warning
        )

    # Oxy nhánh
    if oxygen_type == "nasal":
        return combine_result(
            "🟡 VÀNG - Đang thở oxy nhánh\n➡ PHÒNG THEO DÕI (GẦN CẤP CỨU: P3,4,10,11)",
            "yellow",
            warning
        )

    # Có thuốc nguy cơ
    if len(meds) > 0:
        return combine_result(
            "🟡 VÀNG - Có sử dụng thuốc nguy cơ\n➡ PHÒNG THEO DÕI (GẦN CẤP CỨU: P3,4,10,11)",
            "yellow",
            warning
        )

    # HA cao
    if systolic is not None and diastolic is not None:
        if systolic > 180 or diastolic > 100:
            return combine_result(
                "🟡 VÀNG - Huyết áp cao\n➡ PHÒNG THEO DÕI (GẦN CẤP CỨU: P3,4,10,11)",
                "yellow",
                warning
            )

    # SpO2 giảm nhẹ
    if spo2 is not None and spo2 < 95:
        return combine_result(
            "🟡 VÀNG - SpO2 giảm\n➡ PHÒNG THEO DÕI (GẦN CẤP CỨU: P3,4,10,11)",
            "yellow",
            warning
        )

    # Mạch nhanh
    if pulse is not None and pulse > 110:
        return combine_result(
            "🟡 VÀNG - Nhịp nhanh (theo ECG)\n➡ PHÒNG THEO DÕI (GẦN CẤP CỨU: P3,4,10,11)",
            "yellow",
            warning
        )

    # =====================================
    # 🟢 XANH
    # =====================================

    if not warning and len(meds) == 0:
        return (
            "🟢 XANH - Sinh hiệu ổn định\n➡ PHÒNG THƯỜNG",
            "green"
        )

    return combine_result(
        "⚠️ Chưa đủ dữ kiện phân loại chính xác",
        "normal",
        warning
    )


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

        chest_pain = request.form.get("chest_pain")
        dyspnea = request.form.get("dyspnea")
        gcs_status = request.form.get("gcs")
        stemi = request.form.get("stemi")
        oxygen_type = request.form.get("oxygen_type")

        result, level = classify(
            pulse, systolic, diastolic, spo2,
            meds,
            chest_pain, dyspnea,
            gcs_status,
            stemi,
            oxygen_type
        )

    return render_template("index.html", result=result, level=level)


if __name__ == "__main__":
    app.run(debug=True)