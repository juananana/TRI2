from __future__ import annotations

import io
import json
import unittest
import urllib.error
from unittest import mock

from tri.run_models import (
    ChatClient,
    format_exception,
    normalize_target,
    parse_json,
    run_factorized_schema_compile_then_act,
    run_generic_structured_ledger_then_act,
)
from tri.run_v3_sqlite_trajectories import run_generic as run_sqlite_generic
from tri.run_v3_sqlite_trajectories import run_lifecycle as run_sqlite_lifecycle
from tri.run_v4_policy_models import run_guarded_lifecycle
from tri.lifecycle_ablation import predict as lifecycle_predict
from tri.lifecycle_tasks import task_rows as lifecycle_task_rows
from tri.reference_lifecycle import predict as v2_predict
from tri.tasks import task_rows
from tri.tool_env import ToolEnvironment
from tri.v2_tasks import task_rows as v2_task_rows
from tri.v2_heldout import heldout_rows as v2_heldout_rows
from tri.v3_eval import balanced_smoke_rows, language_cluster_rows, unseen_domain_rows
from tri.v3_factorial_derive import derive_language, derive_sqlite
from tri.v3_cluster_report import bootstrap_clusters, percentile
from tri.v3_cost_report import summarize as summarize_cost
from tri.v3_sqlite_replay import SQLiteWriteEnvironment
from tri.v3_sqlite_trajectory_eval import smoke_rows as trajectory_smoke_rows
from tri.v3_sqlite_trajectory_eval import trajectory_rows
from tri.v3_sqlite_trajectory_report import summarize as summarize_trajectory
from tri.v4_policy_eval import smoke_rows as policy_smoke_rows
from tri.v4_policy_eval import task_rows as policy_task_rows
from tri.v4_policy_report import row_stages as policy_row_stages
from tri.v2_tool_ablation import run_episode as run_v2_episode
from tri.v2_stage_report import row_stages


class TemporalReferentTests(unittest.TestCase):
    def test_task_grid_is_balanced(self) -> None:
        rows = task_rows()
        self.assertEqual(len(rows), 10 * 5 * 2 * 3)
        ids = {r["id"] for r in rows}
        self.assertEqual(len(ids), len(rows))

    def test_flip_conditions_have_different_pre_and_post_targets(self) -> None:
        for row in task_rows():
            if row["update"] == "flip":
                self.assertNotEqual(row["pre_refresh_target"], row["post_refresh_target"])

    def test_anchored_and_dynamic_oracles_differ_only_on_flip(self) -> None:
        rows = task_rows()
        by_key = {(r["domain"], r["paraphrase"], r["binding"], r["update"]): r for r in rows}
        for r in rows:
            other_binding = "dynamic" if r["binding"] == "anchored" else "anchored"
            other = by_key[(r["domain"], r["paraphrase"], other_binding, r["update"])]
            if r["update"] == "flip":
                self.assertNotEqual(r["correct_target"], other["correct_target"])
            elif r["update"] == "stable":
                self.assertEqual(r["correct_target"], other["correct_target"])
            else:
                self.assertNotEqual(r["correct_target"], other["correct_target"])

    def test_removed_anchored_requires_invalid(self) -> None:
        for row in task_rows():
            if row["binding"] == "anchored" and row["update"] == "removed":
                self.assertEqual(row["correct_target"], "INVALID_BOUND_ENTITY")
                self.assertFalse(row["bound_entity_present_after_refresh"])

    def test_parser_helpers(self) -> None:
        self.assertEqual(parse_json('```json\n{"target_id":"INC-104"}\n```')["target_id"], "INC-104")
        self.assertEqual(parse_json('{"tool":"process"}\n{"target_id":"INC-104"}')["tool"], "process")
        self.assertEqual(normalize_target("Please use INC-104."), "INC-104")

    def test_chat_client_retries_transient_http_errors(self) -> None:
        transient = urllib.error.HTTPError(
            "https://example.test", 503, "Service Unavailable", {}, io.BytesIO(b"busy")
        )
        success = io.BytesIO(json.dumps({
            "choices": [{"message": {"content": "ok"}}]
        }).encode())
        client = ChatClient(
            "model", "https://example.test/v1", "key", max_retries=2, retry_backoff=0
        )
        with mock.patch("urllib.request.urlopen", side_effect=[transient, success]):
            self.assertEqual(client.chat([{"role": "user", "content": "hello"}]), "ok")
        self.assertEqual(client.request_attempts, 2)
        self.assertEqual(client.retry_events, 1)

    def test_chat_client_does_not_retry_forbidden(self) -> None:
        forbidden = urllib.error.HTTPError(
            "https://example.test", 403, "Forbidden", {}, io.BytesIO(b"no access")
        )
        client = ChatClient("model", "https://example.test/v1", "key", max_retries=3)
        with mock.patch("urllib.request.urlopen", side_effect=forbidden) as urlopen:
            with self.assertRaises(urllib.error.HTTPError) as caught:
                client.chat([{"role": "user", "content": "hello"}])
        self.assertEqual(urlopen.call_count, 1)
        self.assertIn("no access", format_exception(caught.exception))

    def test_chat_client_can_disable_thinking(self) -> None:
        success = io.BytesIO(json.dumps({
            "choices": [{"message": {"content": "ok"}}]
        }).encode())
        client = ChatClient(
            "model", "https://example.test/v1", "key",
            max_tokens=1200, enable_thinking=False,
        )
        with mock.patch("urllib.request.urlopen", return_value=success) as urlopen:
            self.assertEqual(client.chat([{"role": "user", "content": "hello"}]), "ok")
        payload = json.loads(urlopen.call_args.args[0].data)
        self.assertEqual(payload["max_tokens"], 1200)
        self.assertIs(payload["enable_thinking"], False)

    def test_connection_error_is_classified_as_api_error(self) -> None:
        result = {"errors": [format_exception(ConnectionResetError("remote closed"))]}
        self.assertTrue(result["errors"][0].startswith("api_call_error:"))

    def test_factorized_schema_keeps_reference_and_invalidity_separate(self) -> None:
        task = next(
            row for row in v2_task_rows()
            if row["task_type"] == "scalar" and row["binding"] == "anchored"
            and row["update"] == "invalidate"
        )

        class FakeClient:
            def __init__(self) -> None:
                self.responses = iter([
                    json.dumps({
                        "reference_mode": "preserve",
                        "selector": task["selector"],
                        "bound_target_id": task["pre_refresh_target"],
                        "invalidity_policy": "reject",
                    }),
                    json.dumps({
                        "action": "invalid",
                        "target_id": "INVALID_BOUND_ENTITY",
                    }),
                ])

            def chat(self, messages: list[dict], temperature: float = 0.0) -> str:
                return next(self.responses)

        result = run_factorized_schema_compile_then_act(FakeClient(), task, 0.0)
        self.assertTrue(result["success"])
        self.assertEqual(result["compiled_ledger"]["reference_mode"], "preserve")
        self.assertEqual(result["compiled_ledger"]["invalidity_policy"], "reject")

    def test_generic_structured_ledger_has_no_tri_fields(self) -> None:
        task = next(
            row for row in v2_task_rows()
            if row["task_type"] == "scalar" and row["binding"] == "anchored"
            and row["update"] == "flip"
        )

        class FakeClient:
            def __init__(self) -> None:
                self.responses = iter([
                    json.dumps({
                        "task_goal": task["instruction"],
                        "selected_entity_id": task["pre_refresh_target"],
                        "selected_entity_snapshot": task["initial_state"][0],
                        "selector": task["selector"],
                        "action": task["action"],
                        "action_preconditions": task["action_schema"]["preconditions"],
                    }),
                    json.dumps({"action": "process", "target_id": task["correct_target"]}),
                ])

            def chat(self, messages: list[dict], temperature: float = 0.0) -> str:
                return next(self.responses)

        result = run_generic_structured_ledger_then_act(FakeClient(), task, 0.0)
        self.assertTrue(result["success"])
        self.assertNotIn("reference_mode", result["compiled_ledger"])
        self.assertNotIn("invalidity_policy", result["compiled_ledger"])

    def test_generic_validity_gate_rejects_action_invalid_actor_target(self) -> None:
        task = next(
            row for row in v2_task_rows()
            if row["task_type"] == "scalar" and row["binding"] == "anchored"
            and row["update"] == "invalidate"
        )

        class FakeClient:
            def __init__(self) -> None:
                self.responses = iter([
                    json.dumps({"selected_entity_id": task["pre_refresh_target"]}),
                    json.dumps({"target_id": task["pre_refresh_target"]}),
                ])

            def chat(self, messages: list[dict], temperature: float = 0.0) -> str:
                return next(self.responses)

        result = run_generic_structured_ledger_then_act(
            FakeClient(), task, 0.0, validity_gate=True
        )
        self.assertEqual(result["mode"], "generic_validity_gated_ledger_then_act")
        self.assertEqual(result["predicted_target"], "INVALID_BOUND_ENTITY")
        self.assertTrue(result["success"])

    def test_generic_reference_mode_adds_only_mode_to_generic_ledger(self) -> None:
        task = next(
            row for row in v2_task_rows()
            if row["task_type"] == "scalar" and row["binding"] == "anchored"
            and row["update"] == "flip"
        )

        class FakeClient:
            def __init__(self) -> None:
                self.responses = iter([
                    json.dumps({
                        "task_goal": task["instruction"],
                        "selected_entity_id": task["pre_refresh_target"],
                        "selected_entity_snapshot": task["initial_state"][0],
                        "selector": task["selector"],
                        "action": task["action"],
                        "action_preconditions": task["action_schema"]["preconditions"],
                        "reference_mode": "preserve",
                    }),
                    json.dumps({"action": "process", "target_id": task["correct_target"]}),
                ])

            def chat(self, messages: list[dict], temperature: float = 0.0) -> str:
                return next(self.responses)

        result = run_generic_structured_ledger_then_act(
            FakeClient(), task, 0.0, reference_mode_field=True
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["mode"], "generic_reference_mode_ledger_then_act")
        self.assertEqual(result["compiled_ledger"]["reference_mode"], "preserve")
        self.assertNotIn("invalidity_policy", result["compiled_ledger"])
        self.assertNotIn("guard", result["compiled_ledger"])
        self.assertNotIn("fallback", result["compiled_ledger"])

    def test_factorized_hybrid_gate_does_not_reapply_selector(self) -> None:
        task = next(
            row for row in v2_task_rows()
            if row["task_type"] == "scalar" and row["domain"] == "repo"
            and row["binding"] == "anchored" and row["update"] == "flip"
        )

        class CompilerOnlyClient:
            def __init__(self) -> None:
                self.calls = 0

            def chat(self, messages: list[dict], temperature: float = 0.0) -> str:
                self.calls += 1
                if self.calls > 1:
                    raise AssertionError("preserve branch should not call the actor")
                return json.dumps({
                    "reference_mode": "preserve",
                    "selector": task["selector"],
                    "bound_target_id": task["pre_refresh_target"],
                    "invalidity_policy": "reject",
                })

        client = CompilerOnlyClient()
        result = run_factorized_schema_compile_then_act(
            client, task, 0.0, hybrid_gate=True
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["predicted_target"], task["pre_refresh_target"])
        self.assertTrue(result["symbolic_preserve_gate"])
        self.assertEqual(client.calls, 1)

    def test_tool_environment_refresh_and_process(self) -> None:
        task = next(
            row for row in task_rows()
            if row["domain"] == "incident" and row["paraphrase"] == "p0"
            and row["binding"] == "anchored" and row["update"] == "flip"
        )
        env = ToolEnvironment(task)
        self.assertEqual(env.observe()["entities"], task["initial_state"])
        self.assertEqual(env.refresh()["entities"], task["refreshed_state"])
        self.assertTrue(env.process(task["post_refresh_target"])["ok"])
        self.assertEqual(env.trace[-1]["arguments"]["target_id"], task["post_refresh_target"])

    def test_lifecycle_task_grid_and_oracles(self) -> None:
        rows = lifecycle_task_rows()
        self.assertEqual(len(rows), 30)
        self.assertEqual(len({r["id"] for r in rows}), 30)
        by_key = {(r["domain"], r["paraphrase"], r["binding"]): r for r in rows}
        for row in rows:
            other_binding = "dynamic" if row["binding"] == "anchored" else "anchored"
            other = by_key[(row["domain"], row["paraphrase"], other_binding)]
            self.assertNotEqual(row["correct_target"], other["correct_target"])
            if row["lifecycle_scenario"] == "action_invalid" and row["binding"] == "anchored":
                self.assertEqual(row["correct_target"], "INVALID_BOUND_ENTITY")
                self.assertFalse(row["bound_entity_actionable_after_refresh"])
            if row["lifecycle_scenario"] in {"rename_and_flip", "name_collision"} and row["binding"] == "anchored":
                self.assertEqual(row["correct_target"], row["pre_refresh_target"])

    def test_lifecycle_full_ledger_ablation_is_oracle(self) -> None:
        for row in lifecycle_task_rows():
            self.assertEqual(lifecycle_predict(row, "full_lifecycle_ledger"), row["correct_target"])

    def test_v2_task_grid_has_harder_semantics(self) -> None:
        rows = v2_task_rows()
        self.assertEqual(len(rows), 246)
        self.assertEqual(len({r["id"] for r in rows}), len(rows))
        self.assertTrue(any(r["phenomenon"] == "implicit" for r in rows))
        self.assertTrue(any(r["task_type"] == "collection" for r in rows))
        self.assertTrue(any(r["task_type"] == "nested" for r in rows))
        self.assertTrue(any(r["phenomenon"] == "conditional_validity" for r in rows))
        self.assertTrue(any(r["update"] == "name_collision" for r in rows))

    def test_v2_schema_lifecycle_is_oracle_but_latest_state_is_not(self) -> None:
        rows = v2_task_rows()
        for row in rows:
            self.assertEqual(v2_predict(row, "schema_lifecycle"), row["correct_target"])
        latest_failures = [
            row for row in rows
            if v2_predict(row, "latest_state") != row["correct_target"]
        ]
        self.assertGreater(len(latest_failures), 50)

    def test_v2_app_style_tool_episode_records_trace(self) -> None:
        task = next(
            row for row in v2_task_rows()
            if row["task_type"] == "scalar" and row["binding"] == "anchored"
            and row["update"] == "flip"
        )
        row = run_v2_episode(task, "latest_state")
        self.assertFalse(row["success"])
        self.assertEqual([step["tool"] for step in row["trace"]], ["open_app", "refresh_app", "perform_action"])

    def test_v2_heldout_changes_language_but_preserves_task_semantics(self) -> None:
        dev = {row["id"].replace("v2-", "", 1): row for row in v2_task_rows() if row["task_type"] == "scalar"}
        heldout = v2_heldout_rows()
        self.assertEqual(len(heldout), 160)
        self.assertEqual(len({row["id"] for row in heldout}), 160)
        for row in heldout:
            source = dev[row["id"].replace("v2h-", "", 1)]
            self.assertEqual(row["split"], "heldout")
            self.assertNotEqual(row["instruction"], source["instruction"])
            self.assertEqual(row["initial_state"], source["initial_state"])
            self.assertEqual(row["refreshed_state"], source["refreshed_state"])
            self.assertEqual(row["correct_target"], source["correct_target"])

    def test_v3_language_clusters_are_balanced_and_independent(self) -> None:
        rows = language_cluster_rows()
        self.assertEqual(len(rows), 160)
        self.assertEqual(len({row["id"] for row in rows}), 160)
        self.assertEqual(len({row["template_id"] for row in rows}), 20)
        for template_id in {row["template_id"] for row in rows}:
            cluster = [row for row in rows if row["template_id"] == template_id]
            self.assertEqual(len(cluster), 8)
            self.assertEqual(len({row["domain"] for row in cluster}), 8)
        for style in {row["style"] for row in rows}:
            subset = [row for row in rows if row["style"] == style]
            self.assertEqual(len(subset), 40)
            self.assertEqual({u: sum(row["update"] == u for row in subset) for u in {
                "flip", "stable", "remove", "invalidate", "name_collision"
            }}, {u: 8 for u in {"flip", "stable", "remove", "invalidate", "name_collision"}})

    def test_v3_unseen_domains_have_new_schemas_and_balanced_labels(self) -> None:
        rows = unseen_domain_rows()
        self.assertEqual(len(rows), 80)
        self.assertEqual(len({row["id"] for row in rows}), 80)
        self.assertEqual({row["domain"] for row in rows}, {
            "projects", "expenses", "inventory", "deployments"
        })
        self.assertTrue({row["domain"] for row in rows}.isdisjoint({
            row["domain"] for row in v2_task_rows()
        }))
        for row in rows:
            self.assertEqual(
                row["correct_target"] == "INVALID_BOUND_ENTITY",
                row["binding"] == "anchored"
                and not row["bound_entity_actionable_after_refresh"],
            )

    def test_v3_smoke_crosses_every_style_update_and_template(self) -> None:
        rows = balanced_smoke_rows()
        self.assertEqual(len(rows), 20)
        self.assertEqual(len({row["template_id"] for row in rows}), 20)
        for style in {row["style"] for row in rows}:
            subset = [row for row in rows if row["style"] == style]
            self.assertEqual({row["update"] for row in subset}, {
                "flip", "stable", "remove", "invalidate", "name_collision"
            })

    def test_cluster_bootstrap_resamples_whole_templates(self) -> None:
        clusters = {
            "a": [1, 1, 1, 1],
            "b": [0, 0, 0, 0],
        }
        lo, hi = bootstrap_clusters(
            clusters,
            lambda sample: sum(sample) / len(sample),
            samples=1000,
            seed=7,
        )
        self.assertEqual(lo, 0.0)
        self.assertEqual(hi, 1.0)
        self.assertEqual(percentile([0.0, 1.0], 0.5), 0.5)

    def test_sqlite_environment_enforces_action_preconditions(self) -> None:
        task = next(
            row for row in v2_task_rows()
            if row["task_type"] == "scalar" and row["binding"] == "anchored"
            and row["update"] == "invalidate"
        )
        env = SQLiteWriteEnvironment(task)
        try:
            env.query()
            env.refresh()
            result = env.act(task["pre_refresh_target"])
            self.assertEqual(result["status"], "invalid_target_attempt")
            self.assertEqual(env.acted_ids(), [])
        finally:
            env.close()

    def test_sqlite_environment_records_wrong_entity_write(self) -> None:
        task = next(
            row for row in v2_task_rows()
            if row["task_type"] == "scalar" and row["binding"] == "anchored"
            and row["update"] == "flip"
        )
        env = SQLiteWriteEnvironment(task)
        try:
            env.refresh()
            result = env.act(task["post_refresh_target"])
            self.assertEqual(result["status"], "wrong_entity_write")
            self.assertEqual(env.acted_ids(), [task["post_refresh_target"]])
        finally:
            env.close()

    def test_stage_report_separates_compiler_and_actor_failures(self) -> None:
        task = next(
            row for row in v2_task_rows()
            if row["task_type"] == "scalar" and row["binding"] == "anchored"
            and row["update"] == "flip"
        )
        stages = row_stages({
            "status": "ok",
            "task": task,
            "result": {
                "compiled_ledger": {
                    "reference_mode": "preserve",
                    "bound_target_id": task["pre_refresh_target"],
                    "invalidity_policy": "reject",
                },
                "predicted_target": "INVALID_BOUND_ENTITY",
                "success": False,
                "errors": [],
            },
        })
        self.assertTrue(stages["compiler_correct"])
        self.assertTrue(stages["actor_only_failure"])
        self.assertFalse(stages["compiler_induced_failure"])

    def test_cost_report_uses_logged_requests_and_latency(self) -> None:
        report = summarize_cost([{
            "model": "Qwen/Qwen3.5-122B-A10B",
            "task": {"binding": "anchored"},
            "result": {"mode": "factorized_hybrid_compile_then_act", "errors": []},
            "status": "ok",
            "api_request_attempts": 1,
            "api_retries": 0,
            "latency_s": 1.25,
        }])
        row = report["groups"][0]
        self.assertEqual(row["total_api_requests"], 1)
        self.assertEqual(row["mean_latency_s"], 1.25)

    def test_sqlite_trajectory_subset_is_balanced(self) -> None:
        rows = trajectory_rows()
        self.assertEqual(len(rows), 40)
        self.assertEqual(len({row["id"] for row in rows}), 40)
        self.assertEqual(len({row["template_id"] for row in rows}), 20)
        self.assertEqual(
            {binding: sum(row["binding"] == binding for row in rows)
             for binding in {"anchored", "dynamic"}},
            {"anchored": 20, "dynamic": 20},
        )
        self.assertEqual(
            {update: sum(row["update"] == update for row in rows)
             for update in {"flip", "stable", "remove", "invalidate", "name_collision"}},
            {update: 8 for update in {
                "flip", "stable", "remove", "invalidate", "name_collision"
            }},
        )

    def test_sqlite_trajectory_smoke_covers_domains_styles_and_updates(self) -> None:
        rows = trajectory_smoke_rows()
        self.assertEqual(len(rows), 8)
        self.assertEqual(len({row["domain"] for row in rows}), 8)
        self.assertEqual(
            {style: sum(row["style"] == style for row in rows)
             for style in {row["style"] for row in rows}},
            {style: 2 for style in {row["style"] for row in rows}},
        )
        self.assertEqual({row["update"] for row in rows}, {
            "flip", "stable", "remove", "invalidate", "name_collision"
        })

    def test_model_facing_sqlite_lifecycle_executes_correct_write(self) -> None:
        task = next(
            row for row in trajectory_rows()
            if row["binding"] == "anchored" and row["update"] == "flip"
        )

        class CompilerClient:
            def chat(self, messages: list[dict], temperature: float = 0.0) -> str:
                return json.dumps({
                    "reference_mode": "preserve",
                    "selector": task["selector"],
                    "bound_target_id": task["pre_refresh_target"],
                    "invalidity_policy": "reject",
                })

        result = run_sqlite_lifecycle(CompilerClient(), task, 0.0)
        self.assertTrue(result["final_state_success"])
        self.assertEqual(result["action_status"], "successful_write")
        self.assertEqual(result["acted_ids"], [task["pre_refresh_target"]])
        self.assertEqual(
            [step["tool"] for step in result["tool_trace"]],
            ["query_entities", "query_entities", "refresh_database", "mutate_entity"],
        )

    def test_model_facing_sqlite_generic_records_wrong_write(self) -> None:
        task = next(
            row for row in trajectory_rows()
            if row["binding"] == "anchored" and row["update"] == "flip"
        )

        class ActorClient:
            def __init__(self) -> None:
                self.responses = iter([
                    json.dumps({
                        "selected_entity_id": task["pre_refresh_target"],
                        "selected_entity_snapshot": task["initial_state"][0],
                        "selector": task["selector"],
                        "action": task["action"],
                        "action_preconditions": task["action_schema"]["preconditions"],
                    }),
                    json.dumps({"target_id": task["post_refresh_target"]}),
                ])

            def chat(self, messages: list[dict], temperature: float = 0.0) -> str:
                return next(self.responses)

        result = run_sqlite_generic(ActorClient(), task, 0.0)
        self.assertFalse(result["final_state_success"])
        self.assertEqual(result["action_status"], "wrong_entity_write")
        self.assertEqual(result["acted_ids"], [task["post_refresh_target"]])

    def test_sqlite_lifecycle_free_actor_can_violate_compiled_commitment(self) -> None:
        task = next(
            row for row in trajectory_rows()
            if row["binding"] == "anchored" and row["update"] == "flip"
        )

        class ActorClient:
            def __init__(self) -> None:
                self.responses = iter([
                    json.dumps({
                        "reference_mode": "preserve",
                        "selector": task["selector"],
                        "bound_target_id": task["pre_refresh_target"],
                        "invalidity_policy": "reject",
                    }),
                    json.dumps({"target_id": task["post_refresh_target"]}),
                ])

            def chat(self, messages: list[dict], temperature: float = 0.0) -> str:
                return next(self.responses)

        result = run_sqlite_lifecycle(ActorClient(), task, 0.0, hybrid_gate=False)
        self.assertEqual(result["mode"], "sqlite_lifecycle_free_actor")
        self.assertEqual(result["action_status"], "wrong_entity_write")

    def test_factorial_derivation_reuses_actor_output(self) -> None:
        task = next(
            row for row in trajectory_rows()
            if row["binding"] == "anchored" and row["update"] == "invalidate"
        )
        row = {
            "model": "model",
            "status": "ok",
            "task": task,
            "result": {
                "mode": "generic_structured_ledger_then_act",
                "predicted_target": task["pre_refresh_target"],
                "errors": [],
            },
        }
        language = derive_language(row)
        sqlite = derive_sqlite(row)
        self.assertEqual(language["result"]["predicted_target"], "INVALID_BOUND_ENTITY")
        self.assertEqual(sqlite["result"]["action_status"], "safe_rejection")
        self.assertTrue(sqlite["result"]["derived_from_same_actor_output"])

    def test_sqlite_trajectory_report_counts_real_write_status(self) -> None:
        report = summarize_trajectory([{
            "model": "Qwen/Qwen3.5-122B-A10B",
            "status": "ok",
            "latency_s": 2.0,
            "api_request_attempts": 2,
            "api_retries": 0,
            "result": {
                "mode": "sqlite_generic_structured_ledger",
                "success": False,
                "final_state_success": False,
                "action_status": "wrong_entity_write",
                "collateral_modifications": 1,
                "errors": [],
            },
        }])
        row = report["table"][0]
        self.assertEqual(row["wrong_entity_write"], 1)
        self.assertEqual(row["collateral_modifications"], 1)
        self.assertEqual(row["api_requests"], 2)

    def test_v4_policy_pairs_distinguish_guard_semantics(self) -> None:
        rows = policy_task_rows()
        self.assertEqual(len(rows), 40)
        self.assertEqual(len({row["id"] for row in rows}), 40)
        self.assertEqual(len({row["template_id"] for row in rows}), 10)
        for row in rows:
            if row["update"] in {"flip", "name_collision"}:
                if row["guard_type"] == "action_validity":
                    self.assertEqual(row["correct_target"], row["pre_refresh_target"])
                else:
                    self.assertEqual(row["correct_target"], row["post_refresh_target"])
            if row["update"] in {"remove", "invalidate"}:
                self.assertEqual(row["correct_target"], row["post_refresh_target"])

    def test_v4_policy_smoke_covers_all_template_clusters(self) -> None:
        rows = policy_smoke_rows()
        self.assertEqual(len(rows), 10)
        self.assertEqual(len({row["template_id"] for row in rows}), 10)
        self.assertEqual({row["guard_type"] for row in rows}, {
            "action_validity", "selector_match"
        })

    def test_guarded_lifecycle_gates_action_valid_bound_target(self) -> None:
        task = next(
            row for row in policy_task_rows()
            if row["guard_type"] == "action_validity" and row["update"] == "flip"
        )

        class CompilerClient:
            def __init__(self) -> None:
                self.calls = 0

            def chat(self, messages: list[dict], temperature: float = 0.0) -> str:
                self.calls += 1
                return json.dumps({
                    "reference_mode": "conditional",
                    "guard_type": "action_validity",
                    "selector": task["selector"],
                    "bound_target_id": task["pre_refresh_target"],
                    "fallback_policy": "reevaluate_selector",
                })

        client = CompilerClient()
        result = run_guarded_lifecycle(client, task, 0.0)
        self.assertTrue(result["success"])
        self.assertTrue(result["guard_gate_used"])
        self.assertEqual(client.calls, 1)

    def test_guarded_lifecycle_actor_handles_selector_guard(self) -> None:
        task = next(
            row for row in policy_task_rows()
            if row["guard_type"] == "selector_match" and row["update"] == "flip"
        )

        class CompilerActorClient:
            def __init__(self) -> None:
                self.responses = iter([
                    json.dumps({
                        "reference_mode": "conditional",
                        "guard_type": "selector_match",
                        "selector": task["selector"],
                        "bound_target_id": task["pre_refresh_target"],
                        "fallback_policy": "reevaluate_selector",
                    }),
                    json.dumps({"target_id": task["post_refresh_target"]}),
                ])

            def chat(self, messages: list[dict], temperature: float = 0.0) -> str:
                return next(self.responses)

        result = run_guarded_lifecycle(CompilerActorClient(), task, 0.0)
        self.assertTrue(result["success"])
        self.assertFalse(result["guard_gate_used"])

    def test_v4_stage_report_separates_compiler_and_actor(self) -> None:
        task = policy_task_rows()[0]
        stages = policy_row_stages({
            "model": "Qwen/Qwen3.5-122B-A10B",
            "status": "ok",
            "task": task,
            "result": {
                "mode": "guarded_lifecycle_then_act",
                "compiled_ledger": {
                    "guard_type": task["guard_type"],
                    "bound_target_id": task["pre_refresh_target"],
                },
                "predicted_target": task["post_refresh_target"],
                "success": False,
                "errors": [],
            },
        })
        self.assertTrue(stages["compiler_correct"])
        self.assertTrue(stages["actor_only_failure"])
        self.assertFalse(stages["compiler_induced_failure"])


if __name__ == "__main__":
    unittest.main()
