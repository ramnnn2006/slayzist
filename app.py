import os
from flask import Flask, render_template, request, jsonify
from college_assistant import agent_executor

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    query = request.json.get("query", "").strip()
    if not query:
        return jsonify({"error": "empty query"}), 400
    result = agent_executor.invoke({"input": query})
    return jsonify({"response": result["output"]})

if __name__ == "__main__":
    # use the port the host gives us (Render sets PORT), fall back to 5000 locally
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
