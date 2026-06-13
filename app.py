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
    app.run(debug=True)
