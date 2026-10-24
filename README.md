# onshape_var_convert – Onshape variable converter

Moves variables between **Part Studio variables**, **Variable Studio variables** and **Configuration (quantity)
inputs**, in any direction. Variables are *moved*: written to the destination, re-read to verify, then deleted from the
source.

Mostly by Sonnet 5.5

## Setup

Create an API key at <https://dev-portal.onshape.com> and rename `.env.example` as '.env'
Clone the repo.  
If you will use it a lot recommend `uv tool install [repo-path]` to install as a uv tool, so can run from
terminal anywhere with `onshape-var-convert <ps url> --from --to` command.
Otherwise you need to run from the repo root dir, or provide that path to uv, eg `uv run <path to repo> <ps url>...`


## Exporter

```
onshape-export <document_url> --export dir <export_dir> --name <export filename stem> --zipped <true|false> 
```


## Var-Converter
```
# Convert Part Studio variables -> configuration inputs (same Part Studio)
onshape-var-convert <partstudio-url> --from partstudio --to config --names width,height

# Part Studio / config -> a Variable Studio (found/created by name, then referenced by the Part Studio)
onshape-var-convert <partstudio-url> --from config --to variablestudio --vs-name Variables
onshape-var-convert <partstudio-url> --from partstudio --to variablestudio --target-url <variablestudio-url>

# Variable Studio -> Part Studio variables / configuration inputs (target Part Studio required)
onshape-var-convert <variablestudio-url> --from variablestudio --to partstudio --target-url <partstudio-url>
```

`--dry-run` previews; `--names a,b` selects a subset (default: all).

### Behaviour and limits

- Only LENGTH / ANGLE / NUMBER variables. Others (string, boolean, enum, list, untypable formulas) are skipped and
  reported.
- Configuration defaults must be plain `<number> <unit>` literals; formulas are skipped when converting to config.
  Config min/max are generated (`min(0, v)` .. `10x|v|`).
- A name already present in the destination aborts the run before anything changes.
- Part Studio variables are appended at the end of the feature list.
- Deleting a configuration input may affect features that reference it.
