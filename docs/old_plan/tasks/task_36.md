# Task 36 – Create evaluation harness

**Phase:** Spec‑Driven Integration

**Description:**

Establish a mechanism to evaluate the system’s performance against
representative queries.  Create an `evals/` directory with a
`golden-queries.yaml` file containing a list of queries, the key
points that correct answers should mention and allowed source domains.
Implement a script (or provide clear instructions) that loads this
file, runs the agent on each query, compares the output against the
expected points and produces a report summarizing retrieval accuracy
and citation quality.  Integrate this evaluation into nightly CI
jobs.

**Acceptance Criteria:**

* The `evals/golden-queries.yaml` file exists and follows the
  prescribed schema.
* There is a script or documented procedure to execute the queries
  and evaluate the answers (even if manual).  The evaluation should
  measure whether key points appear and whether citations match
  allowed sources.
* The evaluation harness can be run as part of a scheduled job or
  manual script without user intervention.