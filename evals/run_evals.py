# SPDX-License-Identifier: Apache-2.0
"""Deterministic eval runner for revenue intelligence scorers."""

from __future__ import annotations

import ast
import importlib.util
import re
import sys
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
EVALS_ROOT = ROOT / "evals"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


AQ_SCORER = _load_module(
    "eval_aq_scorer",
    ROOT / "agents" / "anti_qualification_scorer" / "aq_scorer.py",
)
BEST_NEXT = _load_module(
    "eval_best_next_first_dollar",
    ROOT / "plugins" / "ae" / "best_next_first_dollar.py",
)
BOARD_VS_PLAN = _load_module(
    "eval_board_vs_plan_scorer",
    ROOT / "plugins" / "sales-leadership" / "board_vs_plan_scorer.py",
)


class MiniYamlError(ValueError):
    """Raised when a case file uses YAML outside the supported subset."""


def _strip_comment(line: str) -> str:
    in_single = False
    in_double = False
    for i, ch in enumerate(line):
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "#" and not in_single and not in_double:
            return line[:i]
    return line


def _tokenize_yaml(text: str) -> list[tuple[int, str]]:
    rows: list[tuple[int, str]] = []
    for line_no, raw in enumerate(text.splitlines(), start=1):
        if "\t" in raw:
            raise MiniYamlError(f"tabs are not supported at line {line_no}")
        without_comment = _strip_comment(raw).rstrip()
        if not without_comment.strip():
            continue
        indent = len(without_comment) - len(without_comment.lstrip(" "))
        rows.append((indent, without_comment.strip()))
    return rows


def _split_key_value(text: str) -> tuple[str, str | None]:
    if ":" not in text:
        raise MiniYamlError(f"expected key: value, got {text!r}")
    key, value = text.split(":", 1)
    key = key.strip()
    if not key:
        raise MiniYamlError(f"empty key in {text!r}")
    value = value.strip()
    return key, value if value else None


def _split_inline_items(text: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    in_single = False
    in_double = False
    depth = 0
    for ch in text:
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch in "[{" and not in_single and not in_double:
            depth += 1
        elif ch in "]}" and not in_single and not in_double:
            depth -= 1
        elif ch == "," and not in_single and not in_double and depth == 0:
            parts.append("".join(current).strip())
            current = []
            continue
        current.append(ch)
    if current:
        parts.append("".join(current).strip())
    return parts


def _parse_scalar(text: str) -> Any:
    if text in {"null", "Null", "NULL", "~"}:
        return None
    if text in {"true", "True", "TRUE"}:
        return True
    if text in {"false", "False", "FALSE"}:
        return False
    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(part) for part in _split_inline_items(inner)]
    if text.startswith("{") and text.endswith("}"):
        inner = text[1:-1].strip()
        if not inner:
            return {}
        parsed: dict[str, Any] = {}
        for part in _split_inline_items(inner):
            key, value = _split_key_value(part)
            parsed[key] = _parse_scalar(value or "null")
        return parsed
    if (text.startswith('"') and text.endswith('"')) or (
        text.startswith("'") and text.endswith("'")
    ):
        return ast.literal_eval(text)
    if re.fullmatch(r"[-+]?\d+", text):
        return int(text)
    if re.fullmatch(r"[-+]?(\d+\.\d*|\.\d+)([eE][-+]?\d+)?", text) or re.fullmatch(
        r"[-+]?\d+[eE][-+]?\d+",
        text,
    ):
        return float(text)
    return text


def _parse_block(rows: list[tuple[int, str]], index: int, indent: int) -> tuple[Any, int]:
    if index >= len(rows):
        return None, index
    row_indent, text = rows[index]
    if row_indent < indent:
        return None, index
    if row_indent != indent:
        indent = row_indent
    if text.startswith("- "):
        return _parse_list(rows, index, indent)
    return _parse_mapping(rows, index, indent)


def _parse_list(rows: list[tuple[int, str]], index: int, indent: int) -> tuple[list[Any], int]:
    values: list[Any] = []
    while index < len(rows):
        row_indent, text = rows[index]
        if row_indent != indent or not text.startswith("- "):
            break
        item_text = text[2:].strip()
        index += 1
        if not item_text:
            item, index = _parse_block(rows, index, indent + 2)
            values.append(item)
            continue
        if ":" in item_text:
            key, value = _split_key_value(item_text)
            item_map: dict[str, Any] = {}
            if value is None:
                child, index = _parse_block(rows, index, indent + 2)
                item_map[key] = child
            else:
                item_map[key] = _parse_scalar(value)
            while index < len(rows) and rows[index][0] > indent:
                child, index = _parse_block(rows, index, rows[index][0])
                if not isinstance(child, dict):
                    raise MiniYamlError(f"expected mapping under list item {key!r}")
                item_map.update(child)
            values.append(item_map)
        else:
            values.append(_parse_scalar(item_text))
    return values, index


def _parse_mapping(rows: list[tuple[int, str]], index: int, indent: int) -> tuple[dict[str, Any], int]:
    values: dict[str, Any] = {}
    while index < len(rows):
        row_indent, text = rows[index]
        if row_indent != indent or text.startswith("- "):
            break
        key, value = _split_key_value(text)
        index += 1
        if value is None:
            child, index = _parse_block(rows, index, indent + 2)
            values[key] = child
        else:
            values[key] = _parse_scalar(value)
    return values, index


def load_cases(path: Path) -> list[dict[str, Any]]:
    rows = _tokenize_yaml(path.read_text(encoding="utf-8"))
    parsed, index = _parse_block(rows, 0, 0)
    if index != len(rows):
        raise MiniYamlError(f"unparsed content remains in {path}")
    if not isinstance(parsed, list):
        raise MiniYamlError(f"{path} must contain a top-level list")
    for case in parsed:
        if not isinstance(case, dict):
            raise MiniYamlError(f"every case in {path} must be a mapping")
    return parsed


def _failure(message: str, expected: Any = None, actual: Any = None) -> str:
    if expected is None and actual is None:
        return message
    return f"{message}; expected={expected!r}; actual={actual!r}"


def _check_equal(failures: list[str], label: str, expected: Any, actual: Any) -> None:
    if expected != actual:
        failures.append(_failure(label, expected, actual))


def _case_result(case: dict[str, Any], func: Callable[[dict[str, Any]], list[str]]) -> dict[str, Any]:
    failures = func(case)
    return {
        "id": case.get("id"),
        "description": case.get("description"),
        "passed": not failures,
        "failures": failures,
    }


def eval_anti_qualification(case: dict[str, Any]) -> list[str]:
    inputs = dict(case["inputs"])
    expected = case["expected"]
    failures: list[str] = []
    expected_exception = expected.get("raises")
    if expected_exception:
        try:
            AQ_SCORER.score_opportunity(**inputs)
        except Exception as exc:  # noqa: BLE001 - eval reports exception identity.
            if type(exc).__name__ != expected_exception:
                failures.append(_failure("raised exception type", expected_exception, type(exc).__name__))
        else:
            failures.append(_failure("expected exception was not raised", expected_exception, None))
        return failures

    actual = AQ_SCORER.score_opportunity(**inputs)
    for key in ("anti_qual_label", "confidence"):
        if key in expected:
            _check_equal(failures, key, expected[key], actual.get(key))
    if "ratio_approx" in expected:
        ratio = actual.get("anti_qualification_ratio")
        if ratio is None or abs(float(ratio) - float(expected["ratio_approx"])) > 0.01:
            failures.append(_failure("ratio_approx", expected["ratio_approx"], ratio))
    return failures


def _score_or_rank(inputs: dict[str, Any]) -> Any:
    if "opportunities" in inputs:
        return BEST_NEXT.rank_opportunities(inputs["opportunities"])
    return BEST_NEXT.score_opportunity(inputs)


def eval_best_next_first_dollar(case: dict[str, Any]) -> list[str]:
    expected = case["expected"]
    actual = _score_or_rank(case["inputs"])
    failures: list[str] = []

    if "expected_order" in expected:
        order = [row["opportunity_id"] for row in actual]
        _check_equal(failures, "expected_order", expected["expected_order"], order)
        return failures

    if "score_min" in expected or "score_max" in expected:
        score = actual["score"]
        if score < float(expected.get("score_min", 0.0)) or score > float(expected.get("score_max", 100.0)):
            failures.append(_failure("score range", (expected.get("score_min"), expected.get("score_max")), score))
    if "confidence" in expected:
        _check_equal(failures, "confidence", expected["confidence"], actual["confidence"])
    if "score_breakdown" in expected:
        for key, expected_value in expected["score_breakdown"].items():
            actual_value = actual["score_breakdown"].get(key)
            if actual_value != expected_value:
                failures.append(_failure(f"score_breakdown.{key}", expected_value, actual_value))
    return failures


def eval_board_vs_plan(case: dict[str, Any]) -> list[str]:
    inputs = case["inputs"]
    expected = case["expected"]
    actual = BOARD_VS_PLAN.compute_board_delta(
        inputs["constraint_set_a"],
        inputs["constraint_set_b"],
        inputs["opportunities"],
    )
    failures: list[str] = []
    for key in ("set_a_pass_count", "set_b_pass_count"):
        if key in expected:
            _check_equal(failures, key, expected[key], actual[key])
    if "delta_labels" in expected:
        labels = {row["opportunity_id"]: row["delta_label"] for row in actual["delta_opportunities"]}
        _check_equal(failures, "delta_labels", expected["delta_labels"], labels)
    if "largest_bucket" in expected:
        bucket_counts = {
            "PASSED_BOTH": 0,
            "PASSED_A_ONLY": 0,
            "PASSED_B_ONLY": 0,
            "PASSED_NEITHER": 0,
        }
        for row in actual["delta_opportunities"]:
            bucket_counts[row["delta_label"]] += 1
        largest_bucket = max(bucket_counts, key=lambda key: bucket_counts[key])
        _check_equal(failures, "largest_bucket", expected["largest_bucket"], largest_bucket)
    return failures


SUITES: dict[str, Callable[[dict[str, Any]], list[str]]] = {
    "anti_qualification": eval_anti_qualification,
    "best_next_first_dollar": eval_best_next_first_dollar,
    "board_vs_plan": eval_board_vs_plan,
}


def run_suite(path: Path) -> tuple[int, int, list[dict[str, Any]]]:
    suite_name = path.parent.name
    if suite_name not in SUITES:
        raise ValueError(f"unknown eval suite {suite_name!r}")
    cases = load_cases(path)
    results = [_case_result(case, SUITES[suite_name]) for case in cases]
    passed = sum(1 for result in results if result["passed"])
    total = len(results)
    accuracy = (passed / total * 100.0) if total else 0.0
    print(f"{suite_name}: total={total} passed={passed} failed={total - passed} accuracy={accuracy:.1f}%")
    return total, passed, results


def main() -> int:
    case_files = sorted(EVALS_ROOT.glob("*/cases.yaml"))
    if not case_files:
        print("No eval case files found.")
        return 1

    total = 0
    passed = 0
    failed_results: list[dict[str, Any]] = []
    for path in case_files:
        suite_total, suite_passed, results = run_suite(path)
        total += suite_total
        passed += suite_passed
        failed_results.extend(result for result in results if not result["passed"])

    print(f"overall: total={total} passed={passed} failed={total - passed}")
    if failed_results:
        print()
        print("Failed cases:")
        for result in failed_results:
            print(f"- {result['id']}: {result['description']}")
            for failure in result["failures"]:
                print(f"  - {failure}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
