# Harness Machine Version

```
HARNESS_MACHINE_VERSION: 0.2.0
```

## Changelog

### 0.2.0 (2026-03-15)
- Add version infrastructure with HARNESS_MACHINE_VERSION constant
- Add three-tier runtime scaffolds (pico/nano/micro) with 10/13/18 files each
- Add mission-architect and capability-advisor agents (9 total, later 11)
- Add dynamic capability discovery via amplifier module/bundle list
- Add capability picker with markdown checkbox interface
- Add three deployment modes: standalone (cli.py), in-app (api.py), hybrid (service.py)
- Add version stamping in generated config.yaml (generated_version, generated_by)
- Add upgrade system: upgrade-checker agent, upgrade-planner agent, harness-upgrade mode
- Add check-upgrade.yaml and execute-upgrade.yaml recipes
- Add upgrade intake flow (tier, deployment mode, features, system prompt, source migration)
- Add git branch safety for upgrades (upgrade/{version} branch)
- Add revert documentation (git + filesystem)
- Add constraint-spec-template.md with 8 categories of bash attack vectors
- Add docs/DECISION-ARCHITECTURE.md (pico/nano/micro decision-making guide)
- Fix execute-upgrade.yaml recipe schema (name: → id:)
- Fix pyproject.toml version bump in upgrade flow

### 0.1.0 (2026-03-12)
- Initial release: 7 modes, 7 agents, 4 recipes, 3 skills
- Seven-mode pipeline: explore → spec → plan → execute → verify → finish + debug
- Three-agent generation pipeline: generator → critic → refiner
- Constraint engine with refinement decision logic from AutoHarness paper
- Amplifier hook module (modules/hooks-harness) for tool:pre enforcement
- Docker factory templates (Dockerfile, docker-compose, entrypoint, watchdog, monitor)
- 4 reference examples (pico filesystem, developer tooling, domain library, enterprise governance)
