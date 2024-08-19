from flask import Flask, jsonify, request
import logging


logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

@app.route("/fibonacci")
def fibonacci():
    args = request.args
    x = int(args.get("n"))

    assert 1 <= x <= 90
    array = [0, 1]
    for n in range(2, x + 1):
        array.append(array[n - 1] + array[n - 2])

    logging.info("Compute fibonacci(" + str(x) + ") = " + str(array[x]))
    return jsonify(n=x, result=array[x])

app.run(host='0.0.0.0', port=8080)
