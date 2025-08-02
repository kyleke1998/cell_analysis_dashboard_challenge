# Insert Repo Name Here
This is a template repo to build future repositories out of. It contains directories and files common to most Culmination Bio apps. To use this template, click `Create a new repository` from the `Use this template` dropdown in the top right corner.
![Github screenshot for using this template](example.png)

- `.githooks/`, `.flake8`, `.pre-commit-config.yaml` for pre-commit hooks (linting, testing)
- `.github/` including config for `dependabot` as well as a PR template
- `data/` containing common configs for database connections and visuals
- `notebook/` for jupyter notebooks, including
  - `util.ipy` to run the startup scripts in `notebook/scripts/`
- `src/cb/insertRepoNameHere` - The src directory structure for Culmination apps should follow this structure
- `static/` which contains the favicon for Culmination Bio
- `test/` which contains `test/conftest.py` - a basic setup to use `pytest` for unit tests
- standard `.gitignore`
- `environment.yml` for conda environment
= `README.md` - Add information about the repo to the top and delete this portion.

The pieces below are common to most Culmination Bio repositories.

## Installation
### Logging into AWS
- Set the AWS_PROFILE env variable
- Session refresh: ```aws sso login```

### Build environment
- Create a conda environment from the attached environemnt yml:
  ```
  conda env create -f environment.yml
  ```
- Activate with
  ```
  conda activate insertRepoNameHere
  ```
- Add `src` to your `PYTHONPATH`.
  ```
  export PYTHONPATH=/Path/to/insertRepoNameHere/src:$PYTHONPATH
  ```


## Running
Run `notebook/insertRepoNameHere.ipynb`.

## Auto-Format with Pre-Commit Hooks
We use pre-commit hooks configured in `.pre-commit-config.yaml` to format the code. To be able to use the pre-commit hooks, do the following steps:
1. Make sure `pre-commit` is installed by running `pre-commit --version` (it should have automatically installed when creating the conda environment)
2. Run `git config core.hooksPath .githooks` to set the hooks path to the `.githooks` folder in the repo

You only need to do the steps above once for each repo. Now every time you commit a code change, the hooks in `.pre-commit-config.yaml` will execute.

## Contact
* Raymond Luo <raymond@culmination.com>
