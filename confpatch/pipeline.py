"""Pipeline: run a sequence of named steps (patch, transform, validate) on a config."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from confpatch.loaders import load_config, save_config
from confpatch.patch import apply_patch, load_patch
from confpatch.transform import apply_transforms_to_patch
from confpatch.validator import validate_patch_structure


class PipelineError(Exception):
    pass


@dataclass
class StepResult:
    name: str
    success: bool
    message: str = ""

    def __str__(self) -> str:
        status = "ok" if self.success else "fail"
        return f"[{status}] {self.name}: {self.message}"


@dataclass
class PipelineResult:
    config_path: str
    steps: list[StepResult] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return all(s.success for s in self.steps)

    def summary(self) -> str:
        lines = [f"Pipeline for {self.config_path}:"]
        for step in self.steps:
            lines.append(f"  {step}")
        status = "SUCCESS" if self.success else "FAILED"
        lines.append(f"Result: {status}")
        return "\n".join(lines)


def run_pipeline(
    config_path: str,
    steps: list[dict[str, Any]],
    dry_run: bool = False,
) -> PipelineResult:
    """Run a list of step dicts against a config file.

    Each step dict must have 'name' and 'type'. Supported types:
      - patch: requires 'patch_file'
      - transform: requires 'patch_file' and 'transforms' (list of {path, transform})
    """
    result = PipelineResult(config_path=config_path)

    try:
        config = load_config(config_path)
    except FileNotFoundError as exc:
        raise PipelineError(f"Config not found: {config_path}") from exc

    current = dict(config)

    for step in steps:
        name = step.get("name", "unnamed")
        step_type = step.get("type", "")

        try:
            if step_type == "patch":
                patch = load_patch(step["patch_file"])
                validate_patch_structure(patch)
                current = apply_patch(current, patch)
                result.steps.append(StepResult(name=name, success=True, message="patch applied"))

            elif step_type == "transform":
                patch = load_patch(step["patch_file"])
                transforms = step.get("transforms", [])
                patch = apply_transforms_to_patch(patch, transforms)
                validate_patch_structure(patch)
                current = apply_patch(current, patch)
                result.steps.append(StepResult(name=name, success=True, message="transform+patch applied"))

            else:
                raise PipelineError(f"Unknown step type: {step_type!r}")

        except Exception as exc:  # noqa: BLE001
            result.steps.append(StepResult(name=name, success=False, message=str(exc)))
            break

    if result.success and not dry_run:
        save_config(config_path, current)

    return result
