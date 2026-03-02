from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    result = ""

    if request.method == "POST":

        # ===== LẤY DỮ LIỆU =====
        symptoms_list = request.form.getlist("symptoms")
        pulse = request.form.get("pulse")
        bp = request.form.get("bp")
        spo2 = request.form.get("spo2")

        # ===== CHUYỂN ĐỔI SỐ =====
        try:
            pulse = int(pulse) if pulse else None
            spo2 = int(spo2) if spo2 else None

            if bp and "/" in bp:
                systolic = int(bp.split("/")[0])
                diastolic = int(bp.split("/")[1])
            else:
                systolic = None
                diastolic = None

        except:
            pulse = None
            spo2 = None
            systolic = None
            diastolic = None

        # ===== XÁC ĐỊNH SINH HIỆU BÌNH THƯỜNG =====
        pulse_normal = pulse is not None and 60 <= pulse <= 110
        bp_normal = (
            systolic is not None and diastolic is not None and
            systolic >= 90 and diastolic >= 60 and
            systolic <= 180 and diastolic <= 100
        )
        spo2_normal = spo2 is not None and spo2 > 95

        vitals_normal = pulse_normal and bp_normal and spo2_normal

        # =================================================
        # ================= PHÂN LOẠI ====================
        # =================================================

        # 🔴 ĐỎ – Sốc hoặc giảm oxy
        if (systolic is not None and systolic < 90) or \
           (spo2 is not None and spo2 <= 95):

            result = """MỨC ƯU TIÊN: ĐỎ
ĐÁNH GIÁ BAN ĐẦU: Huyết động không ổn định hoặc giảm oxy máu

➡ Xếp bệnh nhân vào phòng cấp cứu"""

            return render_template("index.html", result=result)

        # 🟡 VÀNG – Có đau ngực nhưng sinh hiệu ổn
        if "Đau ngực" in symptoms_list and vitals_normal:

            result = """MỨC ƯU TIÊN: VÀNG
ĐÁNH GIÁ BAN ĐẦU: Đau ngực, sinh hiệu hiện tại ổn định

➡ Xếp bệnh nhân vào phòng theo dõi gần phòng cấp cứu"""

            return render_template("index.html", result=result)

        # 🟢 XANH – Không triệu chứng và sinh hiệu bình thường
        if not symptoms_list and vitals_normal:

            result = """MỨC ƯU TIÊN: XANH
ĐÁNH GIÁ BAN ĐẦU: Không ghi nhận triệu chứng, sinh hiệu bình thường

➡ Xếp phòng không cấp cứu"""

            return render_template("index.html", result=result)

        # Nếu không rơi vào các nhóm trên
        result = """MỨC ƯU TIÊN: VÀNG
ĐÁNH GIÁ BAN ĐẦU: Có dấu hiệu cần theo dõi thêm

➡ Xếp bệnh nhân vào phòng theo dõi"""

    return render_template("index.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)