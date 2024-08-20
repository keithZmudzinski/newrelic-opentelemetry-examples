import logging

from flask import Flask, jsonify, request
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Service name is required for most backends
resource = Resource(attributes = {
    SERVICE_NAME: "getting-started-python-not-env"
})

traceProvider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter())
traceProvider.add_span_processor(processor)
trace.set_tracer_provider(traceProvider)

# Creates a tracer from the global tracer provider
tracer = trace.get_tracer("my.tracer.name")

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

@app.route("/not_instrumented")
def not_instrumented():
    return {'success': True}

@app.route("/fibonacci")
@tracer.start_as_current_span("fibonacci")
def fibonacci():
    args = request.args
    x = int(args.get("n"))

    assert 1 <= x <= 90
    array = [0, 1]
    for n in range(2, x + 1):
        array.append(array[n - 1] + array[n - 2])

    logging.info("Compute fibonacci(" + str(x) + ") = " + str(array[x]))
    return jsonify(n=x, result=array[x])

app.run(host='0.0.0.0', debug=True, port=8080)
