from prometheus_client import Counter, Histogram

processed_count = Counter("sms_processed_total", "Total messages")
success_count = Counter("sms_success_total", "Successful sends")
failure_count = Counter("sms_failure_total", "Failed sends")

latency_hist = Histogram(
    "sms_processing_latency_seconds",
    "Processing latency"
)
