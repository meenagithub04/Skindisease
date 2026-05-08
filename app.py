import os
import json
import os
import json
import random
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image as keras_image
from flask import Flask, request, jsonify, render_template, session,send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

# ================= FLASK APP =================
app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

# ================= CONFIG =================
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
IMG_SIZE = 224

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ================= OPTIONAL MYSQL =================
db = None
cursor = None

try:
    import mysql.connector

    db = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="12345",
        database="skin_disease_db"
    )

    cursor = db.cursor()
    print("✅ MySQL Connected")

except Exception as e:
    print("⚠️ MySQL Not Connected:", e)

# ================= LOAD MODEL =================
# ================= LOAD MODEL =================
model = None
class_names = []

try:
    from tensorflow.keras.models import load_model
    from tensorflow.keras.preprocessing import image as keras_image
    MODEL_PATH = "model/best_skin_model.keras"
    CLASS_FILE = "model/human_labels.json"
    if os.path.exists(MODEL_PATH) and os.path.exists(CLASS_FILE):

        model = load_model(MODEL_PATH)

        with open(CLASS_FILE, "r") as f:
            labels = json.load(f)

        class_names = [labels[str(i)] for i in range(len(labels))]

        print("✅ Model Loaded Successfully")

    else:
        print("⚠️ Model Files Missing")

except Exception as e:
    print("⚠️ TensorFlow Error:", e)

# ================= FOOD DATABASE =================
food_sources = {
    "Vitamin A": "Carrot, Spinach, Sweet Potato",
    "Vitamin B12": "Eggs, Milk, Fish",
    "Vitamin C": "Orange, Lemon, Guava",
    "Vitamin D": "Sunlight, Fish, Egg yolk",
    "Vitamin E": "Almonds, Sunflower seeds",
    "Zinc": "Pumpkin seeds, Meat",
    "Omega 3": "Fish, Flax seeds",
    "Folic Acid": "Spinach, Beans"
}

# ================= DISEASE DATABASE =================
def get_disease_info(disease):
    disease_db = {
        "Acne": {
            "description": "Hair follicles clogged with oil and dead skin.",
            "vitamins_needed": "Vitamin A, Zinc",
            "nutrition_deficiency": "Zinc deficiency affecting oil control",
            "medicine": "Benzoyl Peroxide",
            "severity": "Low"
        },
        "Actinic_Keratosis": {
            "description": "Rough scaly skin patch from sun exposure.",
            "vitamins_needed": "Vitamin C, Vitamin E",
            "nutrition_deficiency": "Antioxidant deficiency",
            "medicine": "Cryotherapy",
            "severity": "Medium"
        },
        "Benign_tumors": {
            "description": "Non-cancerous skin growth.",
            "vitamins_needed": "Vitamin C, Vitamin E",
            "nutrition_deficiency": "Cell growth imbalance",
            "medicine": "Dermatology monitoring",
            "severity": "Low"
        },
        "Bullous": {
            "description": "Fluid-filled blisters.",
            "vitamins_needed": "Vitamin D, Vitamin E",
            "nutrition_deficiency": "Autoimmune inflammation",
            "medicine": "Steroid creams",
            "severity": "Medium"
        },
        "Candidiasis": {
            "description": "Fungal infection.",
            "vitamins_needed": "Vitamin C, Zinc",
            "nutrition_deficiency": "Weak immune system",
            "medicine": "Antifungal medicine",
            "severity": "Medium"
        },
        "DrugEruption": {
            "description": "Drug allergic skin reaction.",
            "vitamins_needed": "Vitamin C",
            "nutrition_deficiency": "Allergic immune response",
            "medicine": "Antihistamines",
            "severity": "Medium"
        },
        "Eczema": {
            "description": "Inflammatory itchy skin condition.",
            "vitamins_needed": "Vitamin D, Vitamin E",
            "nutrition_deficiency": "Skin barrier weakness",
            "medicine": "Moisturizers",
            "severity": "Low"
        },
        "Infestations_Bites": {
            "description": "Skin reaction to insect bites.",
            "vitamins_needed": "Vitamin C",
            "nutrition_deficiency": "Inflammatory reaction",
            "medicine": "Anti-itch cream",
            "severity": "Low"
        },
        "Lichen": {
            "description": "Inflammatory autoimmune skin disease.",
            "vitamins_needed": "Vitamin D, Vitamin B12",
            "nutrition_deficiency": "Immune dysfunction",
            "medicine": "Corticosteroids",
            "severity": "Medium"
        },
        "Lupus": {
            "description": "Autoimmune disease affecting skin.",
            "vitamins_needed": "Vitamin D, Omega 3",
            "nutrition_deficiency": "Autoimmune inflammation",
            "medicine": "Immunosuppressive therapy",
            "severity": "High"
        },
        "Moles": {
            "description": "Pigmented skin growth.",
            "vitamins_needed": "Vitamin C",
            "nutrition_deficiency": "Melanin imbalance",
            "medicine": "Dermatology check",
            "severity": "Low"
        },
        "Psoriasis": {
            "description": "Chronic autoimmune skin disease.",
            "vitamins_needed": "Vitamin D, Omega 3",
            "nutrition_deficiency": "Inflammation imbalance",
            "medicine": "Topical steroids",
            "severity": "Medium"
        },
        "Rosacea": {
            "description": "Facial redness inflammation.",
            "vitamins_needed": "Vitamin B12",
            "nutrition_deficiency": "Skin sensitivity imbalance",
            "medicine": "Metronidazole cream",
            "severity": "Low"
        },
        "Seborrh_Keratoses": {
            "description": "Benign skin growth.",
            "vitamins_needed": "Vitamin E",
            "nutrition_deficiency": "Skin aging",
            "medicine": "Cryotherapy",
            "severity": "Low"
        },
        "SkinCancer": {
            "description": "Abnormal skin cell growth.",
            "vitamins_needed": "Vitamin C, Vitamin E",
            "nutrition_deficiency": "UV radiation damage",
            "medicine": "Immediate dermatologist consultation",
            "severity": "High"
        },
        "Sun_Sunlight_Damage": {
            "description": "Skin damage from UV rays.",
            "vitamins_needed": "Vitamin C, Vitamin E",
            "nutrition_deficiency": "Oxidative stress",
            "medicine": "Sunscreen treatment",
            "severity": "Medium"
        },
        "Tinea": {
            "description": "Ringworm fungal infection.",
            "vitamins_needed": "Vitamin C, Zinc",
            "nutrition_deficiency": "Weak immunity",
            "medicine": "Antifungal cream",
            "severity": "Medium"
        },
        "Vasculitis": {
            "description": "Inflammation of blood vessels.",
            "vitamins_needed": "Vitamin D",
            "nutrition_deficiency": "Immune system inflammation",
            "medicine": "Anti-inflammatory medication",
            "severity": "High"
        },
        "Vitiligo": {
            "description": "White skin patches due to pigment loss.",
            "vitamins_needed": "Vitamin B12, Vitamin D, Folic Acid",
            "nutrition_deficiency": "Melanin pigment deficiency",
            "medicine": "Topical corticosteroids",
            "severity": "Medium"
        },
        "Vascular_Tumors": {
            "description": "Abnormal growth of blood vessel cells in the skin such as hemangiomas.",
            "vitamins_needed": "Vitamin C, Vitamin K",
            "nutrition_deficiency": "Weak blood vessel support and tissue repair imbalance",
            "medicine": "Laser therapy or beta-blocker treatment (consult dermatologist)",
            "severity": "Medium"
        },
        "Warts": {
            "description": "HPV viral infection.",
            "vitamins_needed": "Vitamin C, Zinc",
            "nutrition_deficiency": "Low immunity",
            "medicine": "Salicylic acid",
            "severity": "Low"
        },
        "Unknown_Normal": {
            "description": "Healthy skin.",
            "vitamins_needed": "None",
            "nutrition_deficiency": "None",
            "medicine": "No treatment needed",
            "severity": "None"
        }
    }
    return disease_db.get(disease, {
        "description": "Skin condition detected.",
        "vitamins_needed": "Vitamin C",
        "nutrition_deficiency": "General skin imbalance",
        "medicine": "Consult dermatologist",
        "severity": "Medium"
    })

# ================= FOOD SUGGESTION =================
# ================= FOOD SUGGESTION =================
def get_foods(vitamins):
    if vitamins == "None":
        return []
    foods = []
    for v in vitamins.split(","):
        v = v.strip()
        if v in food_sources:
            foods.extend([f.strip() for f in food_sources[v].split(",")])
    return foods

# ================= IMAGE PREPROCESS =================
def preprocess(img_path):
    img = keras_image.load_img(img_path, target_size=(IMG_SIZE, IMG_SIZE))
    img = keras_image.img_to_array(img)
    img = img / 255.0
    img = np.expand_dims(img, axis=0)
    return img

# ================= MODEL PREDICTION =================
def predict_disease(img_path):
    img = preprocess(img_path)
    preds = model.predict(img)[0]
    best_index = np.argmax(preds)
    disease = class_names[best_index]
    confidence = float(preds[best_index] * 100)
    return disease, round(confidence, 2)

# ================= HELPER =================
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ================= ROUTES =================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload")
@app.route("/upload.html")
def upload():
    return render_template("upload.html")
@app.route("/result")
@app.route("/result.html")
def result():
    return render_template("result.html")


@app.route("/explorer")
@app.route("/explorer.html")
def explorer():
    return render_template("explorer.html")

@app.route("/history")
@app.route("/history.html")
def history():
    return render_template("history.html")

@app.route("/account")
@app.route("/account.html")
def account():
    return render_template("account.html")
# ================= PREDICT =================
@app.route("/predict", methods=["POST"])
def predict():
    try:
        if model is None:
            return jsonify({"error": "Model not loaded"}), 500

        # ===== GET FILE =====
        file = request.files.get("image")
        if not file:
            return jsonify({"error": "No image uploaded"}), 400

        # ===== DEBUG START =====
        print("\n========== DEBUG START ==========")
        print("📥 RAW FORM:", request.form)

        # ===== GET FORM DATA (FIXED) =====
        gender = request.form.get("gender", "Unknown")

        # ✅ FIX: convert age to int properly
        try:
            age = int(request.form.get("age", 0))
        except:
            age = 0

        location = request.form.get("location", "Unknown")
        body_part = request.form.get("body_part", "Unknown")

        print("👤 Gender:", gender)
        print("🎂 Age:", age)
        print("🌍 Location:", location)
        print("🩺 Body Part:", body_part)

        # ===== SAVE IMAGE (ONLY ONCE) =====
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        print("💾 Saved Path:", filepath)

        # ===== PREDICT =====
        disease, confidence = predict_disease(filepath)
        info = get_disease_info(disease)
        foods = get_foods(info["vitamins_needed"])

        print("🧠 Disease:", disease)
        print("📊 Confidence:", confidence)
        print("📖 Description:", info["description"])
        print("💊 Medicine:", info["medicine"])
        print("🥗 Foods:", foods)

        print("========== DEBUG END ==========\n")

               # ===== DIET =====
        diet = [{"food": f, "benefit": "Supports skin recovery", "boost": "+"} for f in foods] \
            if foods else [{"food": "Balanced Diet", "benefit": "General health", "boost": "+"}]

        # ===== MYSQL STORE (SAFE DEBUG) =====
        try:
            if cursor:
                print("💾 INSERTING INTO DATABASE...")

                cursor.execute("""
                    INSERT INTO predictions
                    (gender, age, location, body_part, image_name, disease, accuracy,
                    description, nutrition_deficiency, vitamins_needed,
                    recommended_food, medicine, severity)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    gender or "Unknown",
                    age or 0,
                    location or "Unknown",
                    body_part or "Unknown",
                    filename or "no_image.jpg",
                    disease or "Unknown",
                    confidence or 0.0,

                    info.get("description", "Not available"),
                    info.get("nutrition_deficiency", "Not available"),
                    info.get("vitamins_needed", "None"),

                    ", ".join(foods) if foods else "None",

                    info.get("medicine", "Not available"),
                    info.get("severity", "Low")
                ))

                db.commit()
                print("✅ DATABASE INSERT SUCCESS")

            else:
                print("❌ DATABASE NOT CONNECTED")

        except Exception as db_error:
            print("❌ DB ERROR:", db_error)

        # ===== RESPONSE =====
        return jsonify({
            "diagnosis": disease,
            "confidence": confidence,
            "description": info["description"],
            "severity": info["severity"],

            "patientGender": gender,
            "patientAge": age,
            "patientRegion": location,
            "bodyPart": body_part,

            "treatment": {
                "medication": info["medicine"],
                "application": "Apply as prescribed",
                "frequency": "Twice daily",
                "priority": info["severity"].upper()
            },

            "nutrient_deficiencies": [
                {
                    "nutrient": v.strip(),
                    "level": random.randint(30, 80),
                    "status": "deficient"
                }
                for v in info["vitamins_needed"].split(",")
                if v.strip() != "None"
            ],

            "diet_recommendations": diet,
            "image": filepath
        })

    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({"error": str(e)}), 500
# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)