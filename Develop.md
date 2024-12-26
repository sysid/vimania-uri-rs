# Development
- `maturin` installs rust components in: `.venv/lib/python3.12/site-packages`
- vim expects all packages to be in `pythonx`
- python package development location: `pythonx/vimania_uri_`
- `pythonx/requirements.txt` holds the required python dependencies (copied from `pyproject.toml`)

## Gotcha
- rust crate must be compiled with vim python version
- make sure the correct (python matching) `.so` version is being installed

## Plug config for local development
Load the /Users/tw/dev/s/private/vimania-uri-rs directory:
```bash
Plug '~/dev/vim/vimania-uri-rs'
```
