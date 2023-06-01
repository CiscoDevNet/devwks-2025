from flask import Flask, render_template, request, redirect, jsonify
import os
import requests
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.wsgi import collect_request_attributes
from opentelemetry.propagate import extract
from opentelemetry.sdk import resources
from statistics import mean 

# Service name namespace is required for AppD
resource = resources.Resource(attributes={
    resources.SERVICE_NAME: "pyserver_manual",
    resources.SERVICE_NAMESPACE: "DEVWKS-STUDENT-",# <--- Add your student ID here
    resources.TELEMETRY_SDK_LANGUAGE: "python",
    resources.HOST_NAME : "localhost",
    resources.TELEMETRY_SDK_NAME : "opentelemetry"
})

# Sets the global default tracer provider
trace.set_tracer_provider(TracerProvider(resource=resource))

# Set exporter and add it to the tracer provider
otlp_exporter = OTLPSpanExporter(endpoint="http://127.0.0.1:4318/v1/traces")
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

tracer = trace.get_tracer(__name__)

app = Flask(__name__)

@app.route('/weather', methods=('GET', 'POST'))
def index():
    """
    Flask function to render index.html page + form
    """
    if request.method == 'POST':
        latitude = request.form['latitude']
        longitude = request.form['longitude']

        temp = get_temperature(latitude=latitude,longitude=longitude)
        messages = { "temp" : temp }

        return render_template('index.html', messages=messages)

    return render_template('index.html')

@app.route("/checkweather")
def checkweather():
    """
    Flask server side function to request the temperature from get_temperature function
    """

    with tracer.start_as_current_span(
        name="server_request",
        context=extract(request.headers),
        kind=trace.SpanKind.SERVER,
        attributes=collect_request_attributes(request.environ)
        ):
        latitude = request.args['latitude']
        longitude = request.args['longitude']

        current_span = trace.get_current_span()
        current_span.set_attribute("latitude", str(latitude))
        current_span.set_attribute("longitude", str(longitude))

        temperature = get_temperature(latitude,longitude)
        return jsonify(temperature)


def get_temperature(latitude,longitude):
    """
    weather request via open-meteo APIs with longitude + latitude
    """
    with tracer.start_as_current_span(
        name="weather_request",
        kind=trace.SpanKind.CLIENT):
        try:
            r = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m")
            r_data = r.json()
            temperatures = r_data["hourly"]["temperature_2m"]
            temp_of_day = temperatures[:24]
            average_temp = mean(temp_of_day)
            r_string = average_temp
            return r_string
        except Exception as e:
            r_string = f"Error: {e}"
            return r_string

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
