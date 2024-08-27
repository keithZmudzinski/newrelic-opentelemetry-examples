import logging

from flask import Flask, jsonify, request

from telemetry import instrument_telemetry, record_exception, set_attribute

logging.basicConfig(level=logging.DEBUG)

# Create and instrument app.
app = Flask(__name__)
instrument_telemetry(app)

@app.route("/not_instrumented")
def not_instrumented():
    return {'success': True}

@app.route("/fibonacci")
def fibonacci():
    args = request.args
    x = int(args.get("n"))

    try:
        assert 1 <= x <= 90
    except Exception as exception:
        set_attribute('test', 1337)
        record_exception(exception)

    array = [0, 1]
    for n in range(2, x + 1):
        array.append(array[n - 1] + array[n - 2])

    logging.info("Compute fibonacci(" + str(x) + ") = " + str(array[x]))
    return jsonify(n=x, result=array[x])

app.run(host='0.0.0.0', debug=True, port=8080)
