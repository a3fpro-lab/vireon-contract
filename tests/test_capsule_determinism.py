def _find_and_load_demo_fn(name: str):
    """
    Find a function definition by scanning .py files, then import its *package module*
    by dotted path (e.g. vireon_contract.cli) so relative imports like `from .schema ...` work.
    """
    import sys
    import importlib

    root = Path(__file__).resolve().parents[1]
    src = root / "src"

    # Ensure package imports work in CI
    if src.exists():
        sys.path.insert(0, str(src))
    sys.path.insert(0, str(root))

    # Prefer scanning src/ first
    scan_roots = [src] if src.exists() else []
    scan_roots.append(root)

    needle = f"def {name}("
    candidates = []
    for base in scan_roots:
        for p in base.rglob("*.py"):
            if any(part in {".git", ".venv", "venv", "__pycache__", "site-packages"} for part in p.parts):
                continue
            try:
                txt = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if needle in txt:
                candidates.append(p)

    if not candidates:
        raise ImportError(
            f"Could not find function {name!r} anywhere in the repo. "
            f"Searched under: {', '.join(str(r) for r in scan_roots)}"
        )

    errors = []
    for p in sorted(candidates, key=lambda x: str(x)):
        try:
            # Convert file path -> module dotted path
            if src.exists() and src in p.parents:
                rel = p.relative_to(src)
            else:
                rel = p.relative_to(root)

            parts = list(rel.with_suffix("").parts)
            if parts and parts[-1] == "__init__":
                parts = parts[:-1]
            module_name = ".".join(parts)

            mod = importlib.import_module(module_name)
            fn = getattr(mod, name, None)
            if fn is not None:
                return fn

            errors.append(f"{module_name}: imported but missing {name}")
        except Exception as e:
            errors.append(f"{p}: {type(e).__name__}: {e}")

    raise ImportError(
        f"Found '{name}' in source but could not import any candidate module cleanly.\n"
        + "\n".join(errors[:20])
    )
