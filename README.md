# Frinx Python SDK
This package contains implementation of [Workflow Manager](https://docs.frinx.io/frinx-workflow-manager/introduction/)
client, building blocks for task and workflow definitions and ready-to-use implementations of tasks and workflows,
which cover basic use cases of [FRINX MACHINE](https://docs.frinx.io/) components.

## Environment set up
1. Install poetry
    ```sh
    pip3 install poetry
    ```

2. Install dependencies
     ```sh
    poetry install
    ```

## How to contribute
1. Create new feature branch.
   ```sh
   git checkout -b <branch_name>
   ```

2. Add your changes.
   ```sh
   git add <file>
   ```

3. OPTIONAL - Run pre-commit. Pre-commit triggers linting and static type checker hooks. These checks are also
   triggered by GitHub actions when a PR is created or updated. All errors and warnings raised by linters and
   type checkers must be fixed before the PR can be merged.
   ```sh
   poetry shell
   pre-commit
   ```

4. Commit your changes. We do not enforce commit message structure, but you should follow these
   [best practices](https://cbea.ms/git-commit/).
   ```sh
   git commit
   ```

5. Push your branch to remote repository.
   ```sh
   git push -u origin <branch_name>
   ```
