from __future__ import annotations

import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from scripts.service import CodexService


class CodexServiceTests(unittest.TestCase):
    def make_service(self) -> tuple[CodexService, tempfile.TemporaryDirectory[str]]:
        tempdir = tempfile.TemporaryDirectory()
        accounts_path = Path(tempdir.name) / "accounts.json"
        accounts_path.write_text("{}", encoding="utf-8")
        with patch.object(CodexService, "_kickoff_startup_refresh", lambda self: None):
            service = CodexService(accounts_path=str(accounts_path))
        return service, tempdir

    def test_dashboard_snapshot_orders_accounts_by_priority(self) -> None:
        service, tempdir = self.make_service()
        self.addCleanup(tempdir.cleanup)
        service.save_accounts(
            {
                "due": {
                    "alias": "due",
                    "email": "due@example.com",
                    "plan": "free",
                    "usage_limits": [{"label": "Weekly", "left_percent": 0, "reset_at": "2026-04-13 09:05"}],
                },
                "quota": {
                    "alias": "quota",
                    "email": "quota@example.com",
                    "plan": "free",
                    "usage_limits": [{"label": "Weekly", "left_percent": 42, "reset_at": "2026-04-14 12:00"}],
                },
                "quota_high": {
                    "alias": "quota_high",
                    "email": "quota-high@example.com",
                    "plan": "free",
                    "usage_limits": [{"label": "Weekly", "left_percent": 90, "reset_at": "2026-04-15 12:00"}],
                },
                "vip_quota": {
                    "alias": "vip_quota",
                    "email": "vip-quota@example.com",
                    "plan": "plus",
                    "usage_limits": [{"label": "5h", "left_percent": 42, "reset_at": "2026-04-14 12:30"}],
                },
                "vip": {
                    "alias": "vip",
                    "email": "vip@example.com",
                    "plan": "plus",
                    "usage_limits": [{"label": "5h", "left_percent": 0, "reset_at": "2026-04-14 11:00"}],
                },
                "current": {
                    "alias": "current",
                    "email": "current@example.com",
                    "plan": "free",
                    "account_id": "acct-current",
                    "usage_limits": [{"label": "Weekly", "left_percent": 0, "reset_at": "2026-04-15 08:00"}],
                },
            }
        )

        with patch.object(service, "_current_auth_identity", return_value=("current@example.com", "free", "acct-current")):
            with patch.object(
                service,
                "get_current_account_info",
                return_value={"alias": "current", "email": "current@example.com", "plan": "free", "account_id": "acct-current"},
            ):
                snapshot = service.build_dashboard_snapshot(include_live_current_snapshot=False, refresh_window_minutes=15)

        self.assertEqual(
            [item["alias"] for item in snapshot["accounts"]],
            ["current", "vip_quota", "vip", "quota_high", "quota", "due"],
        )

    def test_refresh_all_accounts_snapshot_refreshes_every_account(self) -> None:
        service, tempdir = self.make_service()
        self.addCleanup(tempdir.cleanup)
        dashboard = {
            "current": {"alias": "alpha", "email": "alpha@example.com", "plan": "plus"},
            "accounts": [
                {"alias": "alpha", "email": "alpha@example.com", "plan": "plus", "account_id": "acct-a", "is_current": True},
                {"alias": "beta", "email": "beta@example.com", "plan": "free", "account_id": "acct-b", "is_current": False},
            ],
        }

        with patch.object(service, "build_dashboard_snapshot", side_effect=[dashboard, dashboard]):
            with patch.object(service, "refresh_current_account_usage_snapshot", return_value={"summary_left": "5h: 66%"}) as current_mock:
                with patch.object(
                    service,
                    "refresh_precise_usage_for_alias",
                    side_effect=lambda alias: {"summary_left": f"{alias}: 88%"},
                ) as precise_mock:
                    result = service.refresh_all_accounts_usage_snapshot(wait_seconds=0.01, retries=1)

        self.assertEqual(result["total"], 2)
        self.assertEqual(result["refreshed"], 2)
        self.assertEqual(result["failed"], 0)
        self.assertEqual(result["accounts"][0]["alias"], "alpha")
        self.assertEqual(result["accounts"][0]["mode"], "local_current")
        self.assertEqual(result["accounts"][1]["alias"], "beta")
        self.assertEqual(result["accounts"][1]["mode"], "remote")
        current_mock.assert_called_once()
        precise_mock.assert_called_once_with("beta")

    def test_current_account_uses_live_plan_for_membership(self) -> None:
        service, tempdir = self.make_service()
        self.addCleanup(tempdir.cleanup)
        service.save_accounts(
            {
                "lxl": {
                    "alias": "lxl",
                    "email": "lxl.getname@gmail.com",
                    "plan": "free",
                    "account_id": "acct-lxl",
                    "usage_limits": [
                        {"label": "5h", "left_percent": 58, "reset_at": "2026-04-17 08:53"},
                        {"label": "Weekly", "left_percent": 100, "reset_at": "2026-04-20 08:53"},
                    ],
                }
            }
        )

        with patch.object(service, "_current_auth_identity", return_value=("lxl.getname@gmail.com", "plus", "acct-lxl")):
            with patch.object(
                service,
                "get_current_account_info",
                return_value={"alias": "lxl", "email": "lxl.getname@gmail.com", "plan": "plus", "account_id": "acct-lxl"},
            ):
                snapshot = service.build_dashboard_snapshot(include_live_current_snapshot=False)

        account = snapshot["accounts"][0]
        self.assertEqual(account["plan"], "plus")
        self.assertTrue(account["is_member"])
        self.assertEqual(account["usage_limits"][0]["label"], "5h")

    def test_five_hour_limit_marks_saved_free_plan_as_member(self) -> None:
        service, tempdir = self.make_service()
        self.addCleanup(tempdir.cleanup)
        service.save_accounts(
            {
                "lxl": {
                    "alias": "lxl",
                    "email": "lxl.getname@gmail.com",
                    "plan": "free",
                    "account_id": "acct-lxl",
                    "subscription_until": "2026-05-01T12:30:00",
                    "usage_limits": [
                        {"label": "5h", "left_percent": 86, "reset_at": "2026-04-13 20:00"},
                        {"label": "Weekly", "left_percent": 56, "reset_at": "2026-04-17 08:53"},
                    ],
                }
            }
        )

        with patch.object(service, "_current_auth_identity", return_value=("lxl.getname@gmail.com", "free", "acct-lxl")):
            with patch.object(
                service,
                "get_current_account_info",
                return_value={"alias": "lxl", "email": "lxl.getname@gmail.com", "plan": "free", "account_id": "acct-lxl"},
            ):
                snapshot = service.build_dashboard_snapshot(include_live_current_snapshot=False)

        account = snapshot["accounts"][0]
        self.assertEqual(snapshot["current"]["plan"], "plus")
        self.assertEqual(account["plan"], "plus")
        self.assertTrue(account["is_member"])
        self.assertEqual(account["subscription_until_text"], "2026-05-01 12:30")

    def test_startup_due_refresh_only_targets_expired_reset_times(self) -> None:
        service, tempdir = self.make_service()
        self.addCleanup(tempdir.cleanup)
        service.save_accounts(
            {
                "expired": {
                    "alias": "expired",
                    "email": "expired@example.com",
                    "plan": "free",
                    "usage_limits": [{"label": "Weekly", "left_percent": 0, "reset_at": "2026-04-13 09:59"}],
                },
                "future": {
                    "alias": "future",
                    "email": "future@example.com",
                    "plan": "free",
                    "usage_limits": [{"label": "Weekly", "left_percent": 0, "reset_at": "2026-04-13 10:01"}],
                },
            }
        )

        due = service._accounts_due_for_refresh(now=datetime(2026, 4, 13, 10, 0))

        self.assertEqual(due, ["expired"])

    def test_startup_auto_refresh_retries_when_quota_is_still_empty(self) -> None:
        service, tempdir = self.make_service()
        self.addCleanup(tempdir.cleanup)
        target = {"alias": "expired", "email": "expired@example.com", "plan": "free"}
        snapshots = [
            {"limits": [{"label": "Weekly", "left_percent": 0, "reset_at": "2026-04-13 10:00"}]},
            {"limits": [{"label": "Weekly", "left_percent": 0, "reset_at": "2026-04-13 10:00"}]},
            {"limits": [{"label": "Weekly", "left_percent": 50, "reset_at": "2026-04-20 10:00"}]},
        ]

        with patch.object(service, "refresh_precise_usage_for_alias", side_effect=snapshots) as refresh_mock:
            with patch("scripts.service.time.sleep") as sleep_mock:
                result = service._refresh_precise_with_startup_retries("expired", target)

        self.assertTrue(result["ok"])
        self.assertEqual(result["attempts"], 3)
        self.assertEqual(refresh_mock.call_count, 3)
        self.assertEqual([call.args[0] for call in sleep_mock.call_args_list], [60.0, 120.0])

    def test_startup_auto_refresh_stops_after_successful_quota(self) -> None:
        service, tempdir = self.make_service()
        self.addCleanup(tempdir.cleanup)
        target = {"alias": "expired", "email": "expired@example.com", "plan": "free"}

        with patch.object(
            service,
            "refresh_precise_usage_for_alias",
            return_value={"limits": [{"label": "Weekly", "left_percent": 50, "reset_at": "2026-04-20 10:00"}]},
        ) as refresh_mock:
            with patch("scripts.service.time.sleep") as sleep_mock:
                result = service._refresh_precise_with_startup_retries("expired", target)

        self.assertTrue(result["ok"])
        self.assertEqual(result["attempts"], 1)
        refresh_mock.assert_called_once_with("expired")
        sleep_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
