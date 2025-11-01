# Spec 34 – Configure spec hygiene tooling

This specification describes how to integrate linting tools to
enforce consistent formatting and clarity in the project’s markdown
documents.  Using tools such as Vale and Markdownlint improves the
quality of prompts, specifications and documentation, making them
easier for LLMs to interpret.

## Steps

1. **Add configuration files.**  At the root of the project,
   create two files:

   - `.vale.ini` – Defines which style guides and checks Vale
     applies.  A minimal configuration might enable general English
     writing rules and disable overly strict warnings.  For example:

     ```ini
     StylesPath = genai-specs/styles
     [*.md]
     BasedOnStyles = Vale, Google
     MinAlertLevel = suggestion
     ```

   - `.markdownlint-cli2.yaml` – Specifies Markdownlint rules.  For
     instance:

     ```yaml
     extends: markdownlint:default
     rules:
       MD013: false  # allow long lines
       MD033: false  # allow inline HTML
     ```

   Modify these configurations to suit the project’s style and
   incorporate additional rule sets as needed.

2. **Install dependencies.**  Add Vale and Markdownlint as
   development dependencies.  In a Python project, you can do this by
   updating `pyproject.toml` or `requirements-dev.txt` with:

   ```
   # requirements-dev.txt
   vale==2.*
   markdownlint-cli2==0.*
   ```

   Alternatively, install them globally on your development machine.

3. **Document usage.**  Update the project’s README or developer
   guide to instruct contributors how to run the linters.  For
   example:

   > Run `vale docs/` and `markdownlint '**/*.md'` to lint documentation.

4. **Integrate with hooks.**  The pre‑patch hook defined in
   `spec_35` will call these linters automatically on changed
   markdown files.  Running the linters locally before committing
   ensures prompt feedback.

## Notes

* Vale uses style rules defined in the `genai‑specs` submodule.
  Ensure `StylesPath` points to the correct directory.  You may need
  to copy or symlink style files into your repository if the
  submodule is not available in all environments.
* Markdownlint rules can be extended or disabled on a file‑by‑file
  basis using inline comments.  See the Markdownlint documentation
  for details.