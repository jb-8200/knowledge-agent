# Observability

This directory contains scripts and documentation for monitoring and
evaluating the knowledge‑base agent during development and
production.  Observability is essential for understanding how
retrieval, synthesis and external search components behave in
practice.

In a mature deployment, you might include:

* **Dashboards** – A Streamlit or Langfuse app that visualizes metrics
  such as retrieval confidence scores, frequency of external search
  invocations, citation accuracy and user feedback trends.
* **Tracing scripts** – Instrumentation to collect request/response
  logs with latency and cost information, optionally using
  OpenTelemetry or LangChain tracing.
* **Evaluation notebooks** – Jupyter notebooks that load evaluation
  data (e.g., golden query results) and generate reports for
  iterative improvement.

At this stage the folder contains only this placeholder README.
Add scripts or notebooks here as the project evolves.