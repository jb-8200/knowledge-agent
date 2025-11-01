# Test Task 36 – Create evaluation harness

## Objective

Verify that a golden‑query evaluation harness exists and can be used to
assess the agent’s answers for correctness and citation quality.

## Steps

1. Confirm that the `evals/` directory exists and contains
   `golden-queries.yaml`.
2. Open `golden-queries.yaml` and verify that each entry defines a
   `query`, `expected_points` list and `allowed_sources` list.
3. Ensure that developer documentation or a script exists describing
   how to run the evaluation harness.  The script should:
   - Load the YAML file.
   - Call the agent for each query.
   - Check for the presence of expected points in the answer.
   - Validate that citations match allowed sources.
   - Produce a summary report.
4. Optionally, run the evaluation harness manually or as part of the
   CI pipeline and verify that it executes without errors.

## Expected Outcome

* The golden queries file exists and follows the prescribed schema.
* Instructions or scripts are available for running evaluations.
* The evaluation harness can execute successfully, producing a
  summary of metrics per query.