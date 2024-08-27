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

def instrument_telemetry(app):
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

    FlaskInstrumentor().instrument_app(app, tracer_provider=traceProvider, meter_provider=meterProvider)

def record_exception(exception):
    current_span = trace.get_current_span()
    current_span.set_status(Status(StatusCode.ERROR))
    current_span.record_exception(exception)

def set_attribute(key, value):
    current_span = trace.get_current_span()
    current_span.set_attribute(key, value)