"""DOW-AIPM-BRD rev 2.1 acceptance tests; synthetic local fixtures only.

Set DOW_REQUIREMENT_EVIDENCE to retain per-case commands, inputs and outputs.
Production files are copied into disposable repositories, never patched in place.
Failures remain failures: these are requirement oracles, not expectedFailure tests.
"""
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
PHRASE = "Start a new project from the DoW AI PM Builder Template and begin Sprint Zero."
AUTHORITIES = ["implementation", "source_admission", "external_tracker_writes",
               "deployment", "real_data_or_api", "cdrl_submission", "risk_acceptance", "control_closure"]


class RequirementAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="dow-req-")
        self.repo = Path(self.tmp.name) / "fixture"
        shutil.copytree(ROOT, self.repo, ignore=shutil.ignore_patterns(
            ".git", ".codex", "__pycache__", ".pytest_cache", "requirement-remediation"))
        self.events = []
        # Synthetic identity scoped to child processes, no global git config.
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("FACTORY_")}
        self.env["FACTORY_CHAIN_ANCHOR_DIR"] = str(Path(self.tmp.name) / "chain-anchors")
        self.env.update(GIT_AUTHOR_NAME="Requirement Fixture", GIT_AUTHOR_EMAIL="fixture@example.invalid",
                        GIT_COMMITTER_NAME="Requirement Fixture", GIT_COMMITTER_EMAIL="fixture@example.invalid")

    def tearDown(self):
        if os.environ.get("DOW_REQUIREMENT_EVIDENCE"):
            out = Path(os.environ["DOW_REQUIREMENT_EVIDENCE"]) / self._testMethodName
            out.mkdir(parents=True, exist_ok=True)
            (out / "commands.json").write_text(json.dumps(self.events, indent=2))
            # Retain the inputs and deterministic outputs that establish case provenance.
            for pattern in [".governance/gate_state.json", "orchestration/tasks.md", "spec.md",
                            "adapter.py", "docs/verification/adapter-capture.json", ".codex/agents/runtime-manifest.json",
                            "docs/verification/factory-runs/*.json", "src/*.py", "new-project/TEMPLATE_PROVENANCE.md"]:
                for src in self.repo.glob(pattern):
                    dst = out / "fixture" / src.relative_to(self.repo)
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(src, dst)
        self.tmp.cleanup()

    def run_command(self, *args, cwd=None, extra=None):
        started = datetime.now(timezone.utc).isoformat()
        result = subprocess.run(args, cwd=cwd or self.repo, env={**self.env, **(extra or {})},
                                capture_output=True, text=True, timeout=45)
        self.events.append(dict(command=list(args), cwd=str(cwd or self.repo), started_utc=started,
                                ended_utc=datetime.now(timezone.utc).isoformat(),
                                environment_overrides=extra or {}, returncode=result.returncode,
                                stdout=result.stdout, stderr=result.stderr))
        return result

    def cli(self, script, *args, extra=None):
        return self.run_command(sys.executable, "automation/" + script + ".py", *args, extra=extra)

    def expect(self, result, code, text=None):
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        if text:
            self.assertIn(text, result.stdout + result.stderr)

    def validate(self):
        return self.cli("validate_template")

    def board(self, **changes):
        task = dict(zip(["Task ID", "Phase", "Status", "Owner Agent", "Required Inputs", "Dependencies",
                         "Acceptance Criteria", "Evidence Required", "Verification Command or Method",
                         "Handoff Target", "Gate Impact"],
                        ["TASK-901", "Discovery", "Ready", "Requirements BA", "synthetic request", "None",
                         "record synthetic notes", "`docs/verification/fixture.md`", "local fixture check",
                         "User Story BA", "none"]))
        task.update(changes)
        text = "#### TASK-901: Synthetic documentation task\n" + "\n".join(
            f"**{key}**: {value}" for key, value in task.items()) + "\n"
        (self.repo / "orchestration/tasks.md").write_text(text)

    def init_git(self):
        for args in [("init", "-q"), ("add", "-A"), ("commit", "-qm", "synthetic fixture")]:
            self.expect(self.run_command("git", *args), 0)

    def adapter(self, body):
        # Packet is present and valid before the child begins its work.
        code = "import json, os, pathlib, sys\n" + \
               "packet_path = pathlib.Path(os.environ['FACTORY_TASK_PACKET'])\n" + \
               "packet = json.loads(packet_path.read_text())\n" + \
               "pathlib.Path('docs/verification/adapter-capture.json').write_text(json.dumps({'packet': str(packet_path), 'task_id': packet['task']['Task ID'], 'stdin': sys.stdin.read()}))\n" + body
        (self.repo / "adapter.py").write_text(code)
        self.init_git()
        command = shlex.join([sys.executable, "adapter.py"])
        return self.cli("governed_factory", "--adapter", "shell", extra={"FACTORY_ADAPTER_COMMAND": command})

    def close_task(self):
        return "p=pathlib.Path('orchestration/tasks.md'); p.write_text(p.read_text().replace('**Status**: Ready', '**Status**: Done'))\n"

    def evidence(self):
        return "pathlib.Path('docs/verification/fixture.md').write_text('Synthetic verification only\\n')\n"

    def result(self):
        paths = list((self.repo / "docs/verification/factory-runs").glob("*-result.json"))
        self.assertEqual(len(paths), 1, str(paths))
        return json.loads(paths[0].read_text())

    def test_SR01_canonical_kickoff_removal_rejected(self):
        p = self.repo / "KICKOFF.md"
        p.write_text(p.read_text().replace(PHRASE, "removed"))
        self.expect(self.validate(), 1, "ERROR KICKOFF.md missing")

    def test_SR02_fresh_project_authority_provenance_and_source_preservation(self):
        self.init_git()
        template_commit = self.run_command("git", "rev-parse", "HEAD").stdout.strip()
        before = {str(p.relative_to(self.repo)): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in self.repo.rglob("*") if p.is_file() and ".git" not in p.parts}
        # Target outside template: init must not touch the template workspace.
        parent = Path(self.tmp.name) / "generated"
        self.expect(self.cli("init_project", "new-project", str(parent)), 0)
        project = parent / "new-project"
        self.expect(self.run_command("git", "rev-parse", "HEAD", cwd=project), 0)
        self.assertTrue((project / ".codex/agents/runtime-manifest.json").is_file())
        state = json.loads((project / ".governance/gate_state.json").read_text())
        self.assertEqual(state["approval_state"], "draft")
        for authority in AUTHORITIES:
            self.assertIs(state[authority + "_authorized"], False)
        for directory in ["src", "services", "packages", "database", "infrastructure", "execution",
                          "docs/handoff", "docs/verification", ".governance", "orchestration"]:
            self.assertTrue((project / directory).is_dir(), directory)
        self.assertEqual((project / "orchestration/system_spec.md").read_bytes(),
                         (self.repo / "orchestration/system-spec-template.md").read_bytes())
        self.assertEqual((project / "orchestration/tasks.md").read_bytes(),
                         (self.repo / "orchestration/task-board-template.md").read_bytes())
        self.assertIn(template_commit, (project / "TEMPLATE_PROVENANCE.md").read_text())
        after = {str(p.relative_to(self.repo)): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in self.repo.rglob("*") if p.is_file() and ".git" not in p.parts}
        self.assertEqual(before, after)
        # Retain provenance separately because the generated project is outside repo.
        (self.repo / "new-project").mkdir()
        shutil.copyfile(project / "TEMPLATE_PROVENANCE.md", self.repo / "new-project/TEMPLATE_PROVENANCE.md")

    @unittest.skip("BLOCKED: actual specialist interview records, mission risk profile and Human Director signoff needed; synthetic records cannot prove SR-03")
    def test_SR03_actual_discovery_sequence_and_human_stop(self):
        pass

    def test_SR04_template_missing_fields_or_placeholders_rejected(self):
        p = self.repo / "spec.md"
        template = (self.repo / "orchestration/system-spec-template.md").read_text()
        for field in ["Project Name", "Status", "System Overview", "Architecture Specification", "Agent Work Packages"]:
            with self.subTest(field=field):
                p.write_text(template.replace(field, "removed"))
                self.expect(self.cli("validate_spec", "--mode", "template", "spec.md"), 1, "missing required field")
        p.write_text("Project Name Status System Overview Architecture Specification Agent Work Packages")
        self.expect(self.cli("validate_spec", "--mode", "template", "spec.md"), 1, "requires explicit placeholders")

    def test_SR04_draft_unlabelled_TBD_rejected(self):
        (self.repo / "spec.md").write_text("Status: Draft\nPurpose: TBD\n")
        self.expect(self.cli("validate_spec", "--mode", "draft", "spec.md"), 1, "requires explicit gap/status label")

    def test_SR04_labelled_draft_accepted(self):
        (self.repo / "spec.md").write_text("Status: Draft\nPurpose: TBD (Gap)\n")
        self.expect(self.cli("validate_spec", "--mode", "draft", "spec.md"), 0)

    def test_SR04_locked_placeholder_and_TBD_rejected(self):
        for value in ["[Inject purpose]", "TBD", "TODO", "Reference Needed", "Pending", "Not Authoritatively Mapped"]:
            with self.subTest(value=value):
                (self.repo / "spec.md").write_text("Purpose: " + value)
                self.expect(self.cli("validate_spec", "--mode", "locked", "spec.md"), 1)

    def test_SR04_locked_explicit_Gap_rejected(self):
        (self.repo / "spec.md").write_text("Purpose: Gap — owner decision outstanding\n")
        self.expect(self.cli("validate_spec", "--mode", "locked", "spec.md"), 1)

    def test_SR04_bounded_unresolved_Gap_markers_rejected(self):
        for value in ["Gap", "Gap: owner decision outstanding", "Gap - owner decision outstanding",
                      "Gap — owner decision outstanding", "Gap – owner decision outstanding", "(Gap)", "[Gap]"]:
            with self.subTest(value=value):
                (self.repo / "spec.md").write_text("Purpose: " + value + "\n")
                self.expect(self.cli("validate_spec", "--mode", "locked", "spec.md"), 1)

    def test_SR04_ordinary_gap_prose_remains_valid(self):
        for value in ["Air gap isolates the synthetic system", "Gap analysis completed", "Gapless record sequence", "No gap remains"]:
            with self.subTest(value=value):
                (self.repo / "spec.md").write_text("Purpose: " + value + "\n")
                self.expect(self.cli("validate_spec", "--mode", "locked", "spec.md"), 0)

    def test_SR04_locked_resolved_spec_accepted(self):
        (self.repo / "spec.md").write_text("Purpose: record synthetic notes\nStatus: Validated\n")
        self.expect(self.cli("validate_spec", "--mode", "locked", "spec.md"), 0)

    def test_SR05_missing_authority_store_defaults_false(self):
        (self.repo / ".governance/gate_state.json").unlink()
        result = self.cli("gatekeeper", "status")
        self.expect(result, 0)
        state = json.loads(result.stdout)
        self.assertEqual(state["approval_state"], "draft")
        for authority in AUTHORITIES:
            self.assertIs(state[authority + "_authorized"], False)

    def test_SR06_all_write_classes_enforced(self):
        for prefix in ["src", "services", "packages", "database", "infrastructure", "execution"]:
            self.expect(self.cli("gatekeeper", "check-action", "--action", "write", "--path", prefix + "/fixture.py"), 2, "DENY")
        for prefix in ["docs", "orchestration", "directives", "requirements", "memory"]:
            self.expect(self.cli("gatekeeper", "check-action", "--action", "write", "--path", prefix + "/fixture.md"), 0, "ALLOW")
        # Authority records are operator-only, even for an authorized agent (JER-39).
        self.expect(self.cli("gatekeeper", "check-action", "--action", "write", "--path", ".governance/gate_state.json"), 2, "DENY")
        self.expect(self.cli("gatekeeper", "check-action", "--action", "write", "--path", ".governance/fixture.md"), 2, "DENY")
        self.expect(self.cli("gatekeeper", "check-action", "--action", "write", "--path", "unknown/fixture"), 2, "DENY")

    def test_SR07_inconsistent_state_blocks_dispatch(self):
        self.board()
        p = self.repo / ".governance/gate_state.json"
        for updates in [{"implementation_authorized": True}, {"approval_state": "approved", "decision": "", "decision_record": ""}]:
            state = json.loads(p.read_text())
            state.update(updates)
            p.write_text(json.dumps(state))
            self.expect(self.cli("gatekeeper", "verify-consistency"), 2, "CONSISTENCY ERROR")
            self.expect(self.cli("governed_factory", "--adapter", "assisted"), 2, "CONSISTENCY ERROR")
            self.assertFalse((self.repo / "docs/verification/factory-runs").exists())

    def test_SR09_each_missing_task_field_and_unknown_owner_rejected(self):
        self.board()
        p = self.repo / "orchestration/tasks.md"
        original = p.read_text()
        for line in original.splitlines()[1:]:
            with self.subTest(field=line.split("**")[1]):
                p.write_text(original.replace(line + "\n", ""))
                self.expect(self.cli("validate_tasks", "orchestration/tasks.md"), 1, "missing task schema field")
        p.write_text(original.replace("Requirements BA", "Unknown Agent"))
        self.expect(self.cli("validate_tasks", "orchestration/tasks.md"), 1, "unknown owner")

    def test_SR10_unknown_owner_refused(self):
        self.board(**{"Owner Agent": "Unknown Agent"})
        self.expect(self.cli("governed_factory", "--adapter", "assisted"), 2, "REFUSAL: unknown accountable owner")

    def test_SR10_incomplete_dependency_stops(self):
        self.board(**{"Dependencies": "TASK-900"})
        self.expect(self.cli("governed_factory", "--adapter", "assisted"), 2, "STOP: dependencies incomplete")

    def test_SR10_human_decision_patterns_stop(self):
        for pattern in ["PM/PO decision", "human authorization", "explicit approval", "phase gate", "gate decision", "director input", "advances gate", "blocks gate"]:
            with self.subTest(pattern=pattern):
                self.board(**{"Acceptance Criteria": pattern})
                self.expect(self.cli("governed_factory", "--adapter", "assisted"), 2, "appears to require human")

    def test_SR10_unauthorized_actions_stop(self):
        for action in ["implementation", "external tracker", "deploy", "CDRL submission"]:
            with self.subTest(action=action):
                self.board(**{"Acceptance Criteria": action})
                self.expect(self.cli("governed_factory", "--adapter", "assisted"), 2, "STOP:")

    def test_SR11_SR12_SR16_shell_packet_contract_and_passing_result(self):
        self.board()
        self.expect(self.adapter(self.evidence() + self.close_task()), 0)
        capture = json.loads((self.repo / "docs/verification/adapter-capture.json").read_text())
        self.assertEqual(capture["task_id"], "TASK-901")
        self.assertIn("NEXT GOVERNED FACTORY TASK: TASK-901", capture["stdin"])
        packet = json.loads(Path(capture["packet"]).read_text())
        self.assertRegex(Path(capture["packet"]).name, r"^\d{8}T\d{6}Z-TASK-901.json$")
        for key in ["task", "gate_state", "required_actions_checked", "non_authorities", "expected_agent_behavior"]:
            self.assertIn(key, packet)
        result = self.result()
        for key in ["record_type", "task_id", "checked_at_utc", "gate_state_at_check", "checks", "outcome"]:
            self.assertIn(key, result)
        self.assertEqual(result["outcome"], "pass")

    def test_SR11_assisted_packet_opt_in(self):
        self.board()
        self.expect(self.cli("governed_factory", "--adapter", "assisted", extra={"FACTORY_RECORD_PACKETS": "true"}), 0, "task packet written")
        self.assertEqual(len(list((self.repo / "docs/verification/factory-runs").glob("*.json"))), 1)

    def test_SR12_missing_shell_command_and_unknown_adapter_refused(self):
        self.board()
        self.expect(self.cli("governed_factory", "--adapter", "shell"), 2, "requires FACTORY_ADAPTER_COMMAND")
        self.expect(self.cli("governed_factory", "--adapter", "unknown"), 2, "REFUSAL: unknown adapter")

    def test_SR08_SR13_unauthorized_write_halts_with_override_record_pointer(self):
        self.board()
        (self.repo / "src").mkdir(exist_ok=True)
        (self.repo / "src/fixture.py").write_text("# initial\n")
        self.expect(self.adapter("pathlib.Path('src/fixture.py').write_text('# changed\\n')\n" + self.evidence() + self.close_task()), 3, "override-register.md")
        result = self.result()
        self.assertEqual(result["outcome"], "violation: unauthorized writes")
        self.assertEqual(result["checks"]["write_audit"]["violations"], ["src/fixture.py"])
        self.assertTrue((self.repo / ".governance/security-compliance/override-register.md").exists())

    def test_SR13_new_untracked_source_directory_detected(self):
        self.board()
        # Unlike an instantiated project, template fixture has no tracked src/.gitkeep.
        self.expect(self.adapter("pathlib.Path('src').mkdir(exist_ok=True)\npathlib.Path('src/new.py').write_text('# synthetic\\n')\n" + self.evidence() + self.close_task()), 3)
        self.assertEqual(self.result()["outcome"], "violation: unauthorized writes")

    def test_SR13_unavailable_git_audit_reported(self):
        self.board(**{"Status": "Done"})
        (self.repo / "docs/verification/fixture.md").write_text("synthetic")
        code = "import sys; sys.path.insert(0, 'automation'); import governed_factory as f; t=f.parse_tasks(f.TASKS_FILE.read_text())[0]; sys.exit(f.post_dispatch_checks(t, {}, None))"
        # A control that cannot run must not report success (JER-37).
        self.expect(self.run_command(sys.executable, "-c", code), 3, "write audit unavailable")
        result = self.result()
        self.assertEqual(result["checks"]["write_audit"], "fail: git unavailable")
        self.assertEqual(result["outcome"], "violation: write audit unavailable")

    def test_SR14_missing_evidence_halts_and_records(self):
        self.board()
        self.expect(self.adapter(self.close_task()), 3, "required evidence missing")
        self.assertEqual(self.result()["outcome"], "violation: missing evidence")

    def test_SR08_missing_evidence_violation_points_to_override_register(self):
        self.board()
        self.expect(self.adapter(self.close_task()), 3, ".governance/security-compliance/override-register.md")

    def test_SR15_open_status_halts_and_records(self):
        self.board()
        self.expect(self.adapter(self.evidence()), 3, "still open after dispatch")
        self.assertEqual(self.result()["outcome"], "violation: no status transition")

    def test_SR08_status_violation_points_to_override_register(self):
        self.board()
        self.expect(self.adapter(self.evidence()), 3, ".governance/security-compliance/override-register.md")

    def test_SR16_nonzero_adapter_still_has_result_record(self):
        self.board()
        self.expect(self.adapter("sys.exit(7)\n"), 7)
        self.result()  # BRD says EVERY autonomous dispatch produces one result, pass or violation.

    def test_SR16_failed_adapter_with_passing_checks_is_not_counted_as_pass(self):
        self.board()
        self.expect(self.adapter(self.evidence() + self.close_task() + "sys.exit(7)\n"), 7)
        result = self.result()
        self.assertEqual(result["adapter_returncode"], 7)
        self.assertEqual(result["outcome"], "violation: adapter failure")
        self.assertEqual(result["violations"], ["adapter failure"])
        self.assertEqual(result["checks"], {"write_audit": "pass", "evidence_exists": "pass", "evidence_changed": "pass",
                                            "status_transitioned": "pass"})
        metrics = self.cli("factory_metrics")
        self.expect(metrics, 0)
        summary = json.loads(metrics.stdout)
        self.assertEqual(summary["runs_recorded"], 1)
        self.assertEqual(summary["runs_passed"], 0)
        self.assertEqual(summary["pass_rate"], 0)

    def test_SR16_adapter_failure_preserves_simultaneous_detective_violations(self):
        self.board()
        (self.repo / "src").mkdir(exist_ok=True)
        (self.repo / "src/fixture.py").write_text("# initial\n")
        self.expect(self.adapter("pathlib.Path('src/fixture.py').write_text('# changed\\n')\nsys.exit(7)\n"), 7)
        result = self.result()
        self.assertEqual(result["outcome"], "violation: adapter failure")
        self.assertEqual(result["adapter_returncode"], 7)
        self.assertEqual(result["violations"], ["unauthorized writes", "missing evidence", "no status transition", "adapter failure"])
        self.assertEqual(result["checks"]["write_audit"]["violations"], ["src/fixture.py"])
        self.assertEqual(result["checks"]["evidence_exists"]["missing"], ["docs/verification/fixture.md"])
        self.assertEqual(result["checks"]["status_transitioned"], "fail: task still open")

    def test_SR13_SR14_SR15_successful_adapter_keeps_first_violation_exit(self):
        self.board()
        (self.repo / "src").mkdir(exist_ok=True)
        (self.repo / "src/fixture.py").write_text("# initial\n")
        self.expect(self.adapter("pathlib.Path('src/fixture.py').write_text('# changed\\n')\n"), 3)
        result = self.result()
        self.assertEqual(result["outcome"], "violation: unauthorized writes")
        self.assertEqual(result["adapter_returncode"], 0)
        self.assertEqual(result["violations"], ["unauthorized writes", "missing evidence", "no status transition"])

    def test_SR08_override_guidance_does_not_grant_authority(self):
        self.board()
        state = self.repo / ".governance/gate_state.json"
        register = self.repo / ".governance/security-compliance/override-register.md"
        before = (state.read_bytes(), register.read_bytes())
        self.expect(self.adapter(self.close_task()), 3, "grants no override or authority")
        self.assertEqual((state.read_bytes(), register.read_bytes()), before)

    def test_SR17_provider_body_drift_rejected(self):
        p = self.repo / "CODEX.md"
        p.write_text(p.read_text() + "\nSynthetic divergent instruction\n")
        self.expect(self.validate(), 1, "provider files out of sync")

    def test_SR18_roster_and_ownership_drift_rejected(self):
        soul = self.repo / ".agent/souls/requirements-ba.md"
        original = soul.read_bytes()
        soul.unlink()
        self.expect(self.validate(), 1, "SOUL roster mismatch")
        soul.write_bytes(original)
        p = self.repo / "subagents/specialization-ownership-map.json"
        own = json.loads(p.read_text())
        del own[next(key for key in own if key.startswith("global/voltagent/"))]
        p.write_text(json.dumps(own))
        self.expect(self.validate(), 1, "ownership missing")

    def test_SR18_stale_claim_rejected(self):
        (self.repo / "docs/synthetic-claim.md").write_text("14 specialized" + " agents")
        self.expect(self.validate(), 1, "ERROR stale string")

    def test_SR19_missing_extra_reordered_and_nonobject_agents_rejected(self):
        runtime = self.repo / ".codex/agents"
        self.expect(self.cli("install_subagents", "subagents/install-config.json", str(runtime)), 0)
        manifest = runtime / "runtime-manifest.json"
        base = json.loads(manifest.read_text())
        agents = base["accountable_agents"]
        for variant in [agents[:-1], agents + [agents[0]], list(reversed(agents)), [a["name"] for a in agents]]:
            with self.subTest(count=len(variant), first=variant[0]):
                manifest.write_text(json.dumps({**base, "accountable_agents": variant}))
                self.expect(self.cli("validate_runtime", str(manifest)), 1, "ERROR:")

    def test_SR19_mandatory_officer_and_materialized_runtime_required(self):
        runtime = self.repo / ".codex/agents"
        self.expect(self.cli("install_subagents", "subagents/install-config.json", str(runtime)), 0)
        manifest = runtime / "runtime-manifest.json"
        base = json.loads(manifest.read_text())
        changed = json.loads(manifest.read_text())
        changed["accountable_agents"][-1]["mandatory"] = False
        manifest.write_text(json.dumps(changed))
        self.expect(self.cli("validate_runtime", str(manifest)), 1, "not marked mandatory")
        manifest.write_text(json.dumps(base))
        (runtime / "requirements-ba.toml").unlink()
        self.expect(self.cli("validate_runtime", str(manifest)), 1, "materialized TOML missing")

    # ---- JER-43 evidence integrity / JER-38 bounded execution -------------

    def factory_config(self, **factory):
        path = self.repo / "factory.config.json"
        cfg = json.loads((self.repo / "factory.config.example.json").read_text())
        limits = factory.pop("limits", {})
        cfg["factory"].update(factory)
        cfg["factory"]["limits"].update(limits)
        path.write_text(json.dumps(cfg))

    def test_empty_evidence_file_is_missing(self):
        self.board()
        self.expect(self.adapter("pathlib.Path('docs/verification/fixture.md').write_text('  \\n')\n" + self.close_task()), 3)
        self.assertEqual(self.result()["outcome"], "violation: missing evidence")

    def test_task_without_evidence_paths_cannot_pass(self):
        self.board(**{"Evidence Required": "a short note"})
        self.expect(self.adapter(self.close_task()), 3, "declares no evidence paths")
        result = self.result()
        self.assertEqual(result["outcome"], "violation: no evidence declared")

    def test_status_flip_without_new_evidence_is_a_violation(self):
        self.board()
        (self.repo / "docs/verification/fixture.md").write_text("old evidence\n")
        self.expect(self.adapter(self.close_task()), 3, "produced no new evidence")
        result = self.result()
        self.assertEqual(result["violations"], ["evidence unchanged"])
        self.assertEqual(result["checks"]["evidence_changed"], "fail: no evidence changed")

    def test_result_records_evidence_hash_output_and_attribution(self):
        self.board()
        body = self.evidence() + self.close_task() + "print('adapter says hello'); print('warned', file=sys.stderr)\n"
        self.expect(self.adapter(body), 0)
        result = self.result()
        digest = hashlib.sha256((self.repo / "docs/verification/fixture.md").read_bytes()).hexdigest()
        self.assertEqual(result["evidence_sha256"], {"docs/verification/fixture.md": digest})
        self.assertIn("adapter says hello", result["adapter_stdout_tail"])
        self.assertIn("warned", result["adapter_stderr_tail"])
        self.assertIn("adapter.py", result["adapter_command"])
        self.assertEqual(result["model_id"], "unreported")
        self.assertIsNone(result["previous_result_sha256"])

    def test_result_chain_detects_edit_and_deletion(self):
        self.board()
        self.expect(self.adapter(self.evidence() + self.close_task()), 0)
        runs = self.repo / "docs/verification/factory-runs"
        first = next(runs.glob("*-result.json"))
        self.expect(self.cli("governed_factory", "--adapter", "assisted"), 0)
        first.write_text(first.read_text().replace('"pass"', '"tampered"', 1))
        self.expect(self.cli("governed_factory", "--adapter", "assisted"), 2, "evidence trail broken")
        first.unlink()
        self.expect(self.cli("governed_factory", "--adapter", "assisted"), 2, "evidence trail broken")

    def test_adapter_timeout_stops_the_run(self):
        self.board()
        self.factory_config(limits={"adapter_timeout_seconds": 2})
        started = datetime.now(timezone.utc)
        self.expect(self.adapter("import time; time.sleep(30)\n"), 124, "adapter exceeded 2s")
        self.assertLess((datetime.now(timezone.utc) - started).total_seconds(), 25)
        result = self.result()
        self.assertTrue(result["adapter_timed_out"])
        self.assertEqual(result["outcome"], "violation: adapter failure")

    def test_stop_on_cannot_drop_or_invent_stops(self):
        self.board()
        stops = json.loads((self.repo / "factory.config.example.json").read_text())["factory"]["stop_on"]
        self.factory_config(stop_on=[s for s in stops if s != "missing_evidence"])
        self.expect(self.cli("governed_factory", "--adapter", "assisted"), 2, "cannot drop mandatory stop missing_evidence")
        self.factory_config(stop_on=stops + ["never"])
        self.expect(self.cli("governed_factory", "--adapter", "assisted"), 2, "unknown stop never")

    def test_loop_stops_at_max_iterations(self):
        self.board()
        (self.repo / "adapter.py").write_text("import pathlib, sys\nsys.stdin.read()\n" + self.evidence() + self.close_task())
        self.init_git()
        command = shlex.join([sys.executable, "adapter.py"])
        result = self.cli("governed_factory", "--adapter", "shell", "--loop", "--max-iterations", "1",
                          extra={"FACTORY_ADAPTER_COMMAND": command})
        self.expect(result, 4, "max_iterations")

    def test_spend_ceiling_requires_reported_usage_and_stops_when_reached(self):
        self.board()
        self.factory_config(limits={"max_tokens": 1000})
        self.expect(self.adapter(self.evidence() + self.close_task()), 3, "reported no usage")
        self.assertEqual(self.result()["outcome"], "violation: budget unverifiable")

    def test_spend_ceiling_reached(self):
        self.board()
        self.factory_config(limits={"max_tokens": 1000})
        usage = "pathlib.Path(os.environ['FACTORY_USAGE_FILE']).write_text(json.dumps({'tokens': 5000}))\n"
        self.expect(self.adapter(self.evidence() + self.close_task() + usage), 3, "spend ceiling reached")
        result = self.result()
        self.assertEqual(result["usage"], {"tokens": 5000})
        self.assertEqual(result["checks"]["budget"]["exceeded"], ["tokens"])

    def test_dirty_protected_tree_stops_before_dispatch(self):
        self.board()
        (self.repo / "adapter.py").write_text(self.close_task())
        self.init_git()
        (self.repo / "src").mkdir(exist_ok=True)
        (self.repo / "src/wip.py").write_text("# operator work in progress\n")
        command = shlex.join([sys.executable, "adapter.py"])
        self.expect(self.cli("governed_factory", "--adapter", "shell", extra={"FACTORY_ADAPTER_COMMAND": command}),
                    2, "dirty_unexpected_state")
        self.assertFalse(list((self.repo / "docs/verification/factory-runs").glob("*-result.json")))

    def test_wiping_run_records_is_detected_by_operator_anchor(self):
        self.board()
        self.expect(self.adapter(self.evidence() + self.close_task()), 0)
        shutil.rmtree(self.repo / "docs/verification/factory-runs")
        self.expect(self.cli("governed_factory", "--adapter", "assisted"), 2, "operator-side chain anchor")

    def test_missing_anchor_for_chained_results_is_detected(self):
        self.board()
        self.expect(self.adapter(self.evidence() + self.close_task()), 0)
        shutil.rmtree(Path(self.env["FACTORY_CHAIN_ANCHOR_DIR"]))
        self.expect(self.cli("governed_factory", "--adapter", "assisted"), 2, "chain anchor")

    def test_adapter_editing_earlier_results_is_a_violation(self):
        self.board()
        self.expect(self.adapter(self.evidence() + self.close_task()), 0)
        self.board(**{"Task ID": "TASK-902"})
        p = self.repo / "orchestration/tasks.md"
        p.write_text(p.read_text().replace("#### TASK-901", "#### TASK-902"))
        tamper = "import glob\nf=sorted(glob.glob('docs/verification/factory-runs/*-result.json'))[0]\npathlib.Path(f).write_text('{}')\n"
        evidence = "pathlib.Path('docs/verification/fixture.md').write_text('second run\\n')\n"
        close = "p=pathlib.Path('orchestration/tasks.md'); p.write_text(p.read_text().replace('**Status**: Ready', '**Status**: Done'))\n"
        self.expect(self.adapter(tamper + evidence + close), 3, "changed or removed during dispatch")

    def test_secrets_are_redacted_from_recorded_output(self):
        self.board()
        leak = ("print('Authorization: Bearer abcdefghijklmnop1234'); print('OPENAI_API_KEY=sk-live-abcdefghijklmnopqrstu')\n"
                "print(json.dumps({'api_key': 'plainsecretvalue99'}))\n")
        self.expect(self.adapter(self.evidence() + self.close_task() + leak), 0)
        tail = self.result()["adapter_stdout_tail"]
        self.assertNotIn("abcdefghijklmnop1234", tail)
        self.assertNotIn("sk-live-abcdefghijklmnopqrstu", tail)
        self.assertNotIn("plainsecretvalue99", tail)
        self.assertIn("[REDACTED]", tail)

    def test_spend_ceiling_needs_the_capped_dimension(self):
        self.board()
        self.factory_config(limits={"max_cost_usd": 1.0})
        usage = "pathlib.Path(os.environ['FACTORY_USAGE_FILE']).write_text(json.dumps({'tokens': 5}))\n"
        self.expect(self.adapter(self.evidence() + self.close_task() + usage), 3, "reported no usage")

    def test_NSR01_stdlib_only_instantiation_on_macos(self):
        # -I ignores environment/user site; -S disables site-packages entirely.
        parent = Path(self.tmp.name) / "stdlib"
        self.expect(self.run_command(sys.executable, "-I", "-S", "automation/init_project.py", "stdlib-fixture", str(parent)), 0)
        self.assertTrue((parent / "stdlib-fixture/.codex/agents/runtime-manifest.json").exists())

    @unittest.skip("NOT RUN: Linux/Windows runners and approved real CLI model runtime qualification are unavailable; deterministic local adapter proves only contract")
    def test_NSR01_cross_platform_and_real_model_runtime_qualification(self):
        pass

    def test_NSR03_synthetic_evidence_chain_survives_local_clone(self):
        self.board(**{"Required Inputs": "`.governance/synthetic-decision.md`"})
        (self.repo / ".governance/synthetic-decision.md").write_text(
            "Synthetic test authorization: TASK-901 documentation only; no implementation authority.\n")
        self.expect(self.adapter(self.evidence() + self.close_task()), 0)
        runs = self.repo / "docs/verification/factory-runs"
        packet_path = next(p for p in runs.glob("*.json") if not p.name.endswith("-result.json"))
        result_path = next(runs.glob("*-result.json"))
        linked = ["orchestration/tasks.md", ".governance/gate_state.json", ".governance/synthetic-decision.md",
                  str(packet_path.relative_to(self.repo)), str(result_path.relative_to(self.repo)), "docs/verification/fixture.md"]
        index = self.repo / "docs/verification/evidence-index.md"
        index.write_text("# Synthetic TASK-901 chain\n" + "\n".join(linked))
        self.expect(self.run_command("git", "add", "-A"), 0)
        self.expect(self.run_command("git", "commit", "-qm", "synthetic evidence chain"), 0)
        clone = Path(self.tmp.name) / "reviewer-clone"
        self.expect(self.run_command("git", "clone", "--no-local", str(self.repo), str(clone)), 0)
        for link in (clone / "docs/verification/evidence-index.md").read_text().splitlines()[1:]:
            self.assertTrue((clone / link).is_file(), link)
            self.expect(self.run_command("git", "ls-files", "--error-unmatch", link, cwd=clone), 0)
        packet = json.loads((clone / packet_path.relative_to(self.repo)).read_text())
        result = json.loads((clone / result_path.relative_to(self.repo)).read_text())
        self.assertEqual(packet["task"]["Task ID"], result["task_id"])
        self.assertFalse(packet["gate_state"]["implementation_authorized"])
        self.assertEqual(result["outcome"], "pass")

    @unittest.skip("INSPECTION ONLY: real work-product/task/authorization/gate/evidence-index chain is not populated in this template; synthetic clone test does not close NSR-03")
    def test_NSR03_actual_project_chain_review(self):
        pass


if __name__ == "__main__":
    unittest.main()
