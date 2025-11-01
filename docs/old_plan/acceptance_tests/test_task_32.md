# Test Task 32 – Set up work‑item YAML definitions

## Objective

Ensure that the `.work-items/` directory exists and contains properly
structured YAML work‑item files.

## Steps

1. Check that a hidden directory named `.work-items/` exists at the
   project root.
2. List the files inside `.work-items/` and verify that each file has
   a `.yaml` extension.
3. For each work‑item file, load its contents as YAML and confirm
   that it contains the required keys: `id`, `user_story`,
   `description`, `spec_refs`, `acceptance_tests` and `code_targets`.
4. Open `001_bootstrap_spec.yaml` and verify that it references
   `spec_31`, `test_task_31.md` and relevant code targets.

## Expected Outcome

The following conditions should hold:

* The `.work-items/` directory exists and includes at least one YAML file.
* Every work‑item YAML file defines all required keys and uses lists for
  `spec_refs`, `acceptance_tests` and `code_targets`.
* The example work‑item correctly links the bootstrap specification and test.