# Harness Machine Version

```
HARNESS_MACHINE_VERSION: 0.2.0
```

## Changelog

### 0.2.0 (2026-03-15)

- Add version infrastructure (`context/version.md`) with HARNESS_MACHINE_VERSION constant
- Add `config.yaml.template` for all three tiers (pico/nano/micro) with version stamping fields
- Add Deployment Mode enum to `harness-format.md` (standalone/in-app/hybrid)
- Add entry points table for all three deployment modes
- Add Version Stamping spec section to `harness-format.md` with `generated_by` field
- Bump bundle version from 0.1.0 to 0.2.0 in `bundle.md` and `behaviors/harness-machine.yaml`

### 0.1.0 (initial)

- Initial release with 9 agents, 7 modes, 4 recipes, 3 skills
- Three size tiers: pico / nano / micro
- Dynamic capability discovery and mission-based naming
- Three runtime scaffolds with standalone CLI and Docker support
