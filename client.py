# This script is mainly for creating telemetry data

import os
import requests
from opentelemetry import trace
from opentelemetry.propagate import inject
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk import resources
import time
import random

# Service name namespace is required for AppD
resource = resources.Resource(attributes={
    resources.SERVICE_NAME: "pyclient",
    resources.SERVICE_NAMESPACE: "weatherapp",
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

def check_weather_auto(latitude,longitude):
    """
    Check temperature on the auto instrumentation flask server
    """
    with tracer.start_as_current_span(
        name="client_request_auto",
        kind=trace.SpanKind.CLIENT,
        attributes={
            SpanAttributes.HTTP_METHOD : "GET",
            SpanAttributes.HTTP_USER_AGENT : "Client Python Script"
        }):
        headers = {}
        inject(headers)
        requests.get(f"http://127.0.0.1:5001/checkweather?latitude={latitude}&longitude={longitude}",headers=headers)

def check_weather_manual(latitude,longitude):
    """
    Check temperature on the manual instrumented flask server
    """
    with tracer.start_as_current_span(
        name="client_request_manual",
        kind=trace.SpanKind.CLIENT,
        attributes={
            SpanAttributes.HTTP_METHOD : "GET",
            SpanAttributes.HTTP_USER_AGENT : "Client Python Script"
        }):
        headers = {}
        inject(headers)
        requests.get(f"http://127.0.0.1:5000/checkweather?latitude={latitude}&longitude={longitude}",headers=headers)

def url_checker(url):
    try:
        #Get Url
        get = requests.get(url)
        #if the request succeeds
        if get.status_code == 200:
            return(f"{url}: is reachable")
        else:
            return(f"{url}: is Not reachable, status_code: {get.status_code}")
        
    except requests.exceptions.RequestException as e:
        # print URL with Errors
        raise SystemExit(f"{url}: is Not reachable \nErrr: {e}")

time.sleep(5) #wait 5s until the servers are up


while True:
    """
    Create random coordinates and ask the weather there
    """
    lat = random.randint(-90,90)
    long = random.randint(-180,180)

    check_weather_auto(lat,long)
    time.sleep(1)
    check_weather_manual(lat,long)
