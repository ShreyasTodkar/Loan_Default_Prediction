from flask import Flask, render_template, request, jsonify
import mysql.connector
import onnxruntime as ort
import numpy as np
import os
import traceback

# Initialize Flask
app = Flask(__name__, template_folder="templates", static_folder="static")

# MySQL Configuration (better to move into config.py or .env)
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "aladin51",
    "database": "loan_default"
}

def connect_db():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Database connection failed: {err}")
        return None

# Load ONNX model (relative path)
# Load ONNX model (absolute path)
onnx_model_path = r"D:\Shreyas_Todkar\CDAC\Project\Datasets\New_Data\loan_default_spark_xgb_model.onnx"
onnx_session = ort.InferenceSession(onnx_model_path)
input_name = onnx_session.get_inputs()[0].name
output_name = onnx_session.get_outputs()[0].name


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        # Ensure all values are floats
        features = [
            float(data["age"]),
            float(data["income"]),
            float(data["loanAmount"]),
            float(data["creditScore"]),
            float(data["monthsEmployed"]),
            float(data["interestRate"]),
            float(data["dtiRatio"]),
            float(data["loanTerm"])
        ]

        input_features = np.array([features], dtype=np.float32)

        # Predict
        prediction = onnx_session.run([output_name], {input_name: input_features})
        predicted_value = int(prediction[0][0])

        result_message = (
            "You cannot apply for the loan." if predicted_value == 1
            else "You can apply for the loan."
        )

        # Save to database
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            sql = """
                INSERT INTO loan_applications
                (age, income, loanAmount, creditScore, monthsEmployed, interestRate, dtiRatio, loanTerm, prediction)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """
            cursor.execute(sql, (*features, predicted_value))
            conn.commit()
            cursor.close()
            conn.close()

        return jsonify({"prediction": predicted_value, "message": result_message})

    except Exception as e:
        return jsonify({"error": traceback.format_exc()}), 500

if __name__ == "__main__":
    app.run(debug=True)