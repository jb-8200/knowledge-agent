# Spec 31 – Import genai‑specs and create rules directory

This specification describes how to add the `genai‑specs` repository
and prepare the rules directory for spec‑driven development.

## Steps

1. **Add the submodule.**  Run the following command at the project
   root:
   ```sh
   git submodule add https://github.com/betsalel-williamson/genai-specs
   ```
   This command will create a `genai-specs` directory tracked at a
   specific commit.  Commit the `.gitmodules` file as well.

2. **Copy or link core files.**  The following files from the
   submodule should be copied or symlinked into the `rules/`
   directory:
   - `process-01.mdc`, `process-02.mdc`, `process-03.mdc`,
     `process-04.mdc`, `process-05.mdc`
   - `standards-design.mdc`
   - `standards-task.mdc`
   - `standards-architecture.mdc`
   - `standards-decision.mdc`

   Use symbolic links (`ln -s`) to avoid duplicating content, or copy
   the files if symlinks are not supported by your platform.

3. **Document update procedure.**  In `rules/README.md`, describe how
   to update these files when the submodule is updated (i.e., run
   `git submodule update --remote` and refresh the links).

## Notes

* The submodule should track a specific commit rather than the
  repository head to ensure reproducible builds.
* Additional files from `genai‑specs` can be linked on a conditional
  basis (e.g., language-specific standards).