from pathlib import Path

from src.patches import register_patch


@register_patch(name="disable_analytics", description="Disables Firebase/Analytics in buildozer.spec")
def disable_analytics(buildozer_path: Path, **kwargs):
    spec_path = buildozer_path.parent / "buildozer.spec"
    if not spec_path.exists():
        return
    content = spec_path.read_text(encoding="utf-8")
    content = content.replace("#analytics", "# analytics")
    spec_path.write_text(content, encoding="utf-8")
