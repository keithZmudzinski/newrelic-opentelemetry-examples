import logging

from flask import Flask, jsonify, request
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter


resource = Resource(attributes = {
    SERVICE_NAME: 'getting-started-python-not-env'
})

# Add tracing.
traceProvider = TracerProvider(resource=resource)
nr_processor = BatchSpanProcessor(OTLPSpanExporter())
console_processor = BatchSpanProcessor(ConsoleSpanExporter())
traceProvider.add_span_processor(nr_processor)
traceProvider.add_span_processor(console_processor)
trace.set_tracer_provider(traceProvider)

# Add metrics.
reader = PeriodicExportingMetricReader(OTLPMetricExporter())
meterProvider = MeterProvider(resource=resource, metric_readers=[reader])

logging.basicConfig(level=logging.DEBUG)

# Create and instrument app.
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app, tracer_provider=traceProvider, meter_provider=meterProvider)

@app.route("/not_instrumented")
def not_instrumented():
    return {'success': True}

@app.route("/fibonacci")
def fibonacci():
    args = request.args
    x = int(args.get("n"))

    try:
        assert 1 <= x <= 90
    except Exception as error:
        current_span = trace.get_current_span()
        current_span.set_status(Status(StatusCode.ERROR))
        current_span.record_exception(error)

    array = [0, 1]
    for n in range(2, x + 1):
        array.append(array[n - 1] + array[n - 2])

    logging.info("Compute fibonacci(" + str(x) + ") = " + str(array[x]))
    return jsonify(n=x, result=array[x])

app.run(host='0.0.0.0', debug=True, port=8080)
