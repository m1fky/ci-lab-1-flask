from flask import Flask, jsonify, request


def create_app():
    app = Flask(__name__)

    @app.route("/health")
    def health():
        return jsonify(status="ok"), 200

    @app.route("/sum")
    def sum_numbers():
        a = request.args.get("a", type=int)
        b = request.args.get("b", type=int)
        if a is None or b is None:
            return jsonify(error="parameters a and b are required"), 400
        return jsonify(result=a + b), 200

    return app
