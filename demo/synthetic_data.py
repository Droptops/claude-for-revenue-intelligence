# SPDX-License-Identifier: Apache-2.0
"""Synthetic inputs for the morning dossier demo."""

from __future__ import annotations


AVG_CYCLE_DAYS = 45


ACCOUNTS = [
    {
        "account_id": "ACCOUNT_LABEL_1",
        "segment": "mid-market",
        "motion": "new-logo",
        "observable_size_band": "500-1000 employees",
    },
    {
        "account_id": "ACCOUNT_LABEL_2",
        "segment": "enterprise",
        "motion": "expansion",
        "observable_size_band": "1000-5000 employees",
    },
    {
        "account_id": "ACCOUNT_LABEL_3",
        "segment": "commercial",
        "motion": "renewal-adjacent",
        "observable_size_band": "100-500 employees",
    },
]


OPPORTUNITIES = [
    {
        "account_id": "ACCOUNT_LABEL_1",
        "opportunity_id": "OPP_LABEL_101",
        "outcome": "OPEN",
        "stage": "Evaluation",
        "days_in_stage": 78,
        "last_touch_days": 12,
        "deal_size": 180000.0,
        "cycle_days": 82,
        "consulting_spend": 520000.0,
        "implementation_spend": 130000.0,
        "data_source": "CRM",
        "clone_profile_match": True,
        "trigger_event_count": 2,
        "persona_coverage_score": 0.55,
        "outcome_signal": "WEAK",
        "outlier_flag": False,
        "outlier_reason": "",
    },
    {
        "account_id": "ACCOUNT_LABEL_1",
        "opportunity_id": "OPP_LABEL_102",
        "outcome": "CW",
        "stage": "Closed Won",
        "days_in_stage": 18,
        "last_touch_days": 5,
        "deal_size": 95000.0,
        "cycle_days": 41,
        "consulting_spend": 60000.0,
        "implementation_spend": 140000.0,
        "data_source": "CRM",
        "clone_profile_match": True,
        "trigger_event_count": 1,
        "persona_coverage_score": 0.72,
        "outcome_signal": "STRONG",
        "outlier_flag": False,
        "outlier_reason": "",
    },
    {
        "account_id": "ACCOUNT_LABEL_2",
        "opportunity_id": "OPP_LABEL_201",
        "outcome": "OPEN",
        "stage": "Business case",
        "days_in_stage": 34,
        "last_touch_days": 4,
        "deal_size": 260000.0,
        "cycle_days": 58,
        "consulting_spend": 240000.0,
        "implementation_spend": 160000.0,
        "data_source": "MIXED",
        "clone_profile_match": True,
        "trigger_event_count": 3,
        "persona_coverage_score": 0.82,
        "outcome_signal": "STRONG",
        "outlier_flag": False,
        "outlier_reason": "",
    },
    {
        "account_id": "ACCOUNT_LABEL_2",
        "opportunity_id": "OPP_LABEL_202",
        "outcome": "OPEN",
        "stage": "Discovery",
        "days_in_stage": 16,
        "last_touch_days": 2,
        "deal_size": 70000.0,
        "cycle_days": 24,
        "consulting_spend": 30000.0,
        "implementation_spend": 120000.0,
        "data_source": "CRM_PARTIAL",
        "clone_profile_match": False,
        "trigger_event_count": 1,
        "persona_coverage_score": 0.35,
        "outcome_signal": "UNKNOWN",
        "outlier_flag": False,
        "outlier_reason": "",
    },
    {
        "account_id": "ACCOUNT_LABEL_3",
        "opportunity_id": "OPP_LABEL_301",
        "outcome": "OPEN",
        "stage": "Proposal",
        "days_in_stage": 91,
        "last_touch_days": 29,
        "deal_size": 135000.0,
        "cycle_days": 112,
        "consulting_spend": 160000.0,
        "implementation_spend": 100000.0,
        "data_source": "ESTIMATED",
        "clone_profile_match": False,
        "trigger_event_count": 0,
        "persona_coverage_score": 0.25,
        "outcome_signal": "NONE",
        "outlier_flag": True,
        "outlier_reason": "stage skipped without prerequisite milestone",
    },
    {
        "account_id": "ACCOUNT_LABEL_3",
        "opportunity_id": "OPP_LABEL_302",
        "outcome": "CL",
        "stage": "Closed Lost",
        "days_in_stage": 22,
        "last_touch_days": 40,
        "deal_size": 54000.0,
        "cycle_days": 38,
        "consulting_spend": 210000.0,
        "implementation_spend": 70000.0,
        "data_source": "CRM",
        "clone_profile_match": False,
        "trigger_event_count": 0,
        "persona_coverage_score": 0.18,
        "outcome_signal": "NONE",
        "outlier_flag": False,
        "outlier_reason": "",
    },
]


PERSONAS = [
    {
        "account_id": "ACCOUNT_LABEL_1",
        "person_id": "person_id_a",
        "influence_tier": 1,
        "role_label": "economic buyer",
        "engagement_status": "DARK",
        "last_touch_days": 41,
    },
    {
        "account_id": "ACCOUNT_LABEL_1",
        "person_id": "person_id_b",
        "influence_tier": 2,
        "role_label": "technical evaluator",
        "engagement_status": "ENGAGED",
        "last_touch_days": 9,
    },
    {
        "account_id": "ACCOUNT_LABEL_2",
        "person_id": "person_id_c",
        "influence_tier": 1,
        "role_label": "economic buyer",
        "engagement_status": "ENGAGED",
        "last_touch_days": 3,
    },
    {
        "account_id": "ACCOUNT_LABEL_2",
        "person_id": "person_id_d",
        "influence_tier": 1,
        "role_label": "operations sponsor",
        "engagement_status": "UNCONTACTED",
        "last_touch_days": None,
    },
    {
        "account_id": "ACCOUNT_LABEL_3",
        "person_id": "person_id_e",
        "influence_tier": 1,
        "role_label": "economic buyer",
        "engagement_status": "DARK",
        "last_touch_days": 62,
    },
    {
        "account_id": "ACCOUNT_LABEL_3",
        "person_id": "person_id_f",
        "influence_tier": 2,
        "role_label": "renewal operator",
        "engagement_status": "ENGAGED",
        "last_touch_days": 14,
    },
]


TRIGGER_EVENTS = [
    {
        "account_id": "ACCOUNT_LABEL_1",
        "signal_class": "EARNINGS_LANGUAGE",
        "signal_family": "contraction",
        "confidence_score": 0.50,
        "signal_summary": "Budget language shifted toward cost control and delayed discretionary spend.",
        "source_url": "https://placeholder.invalid/events/account-label-1",
    },
    {
        "account_id": "ACCOUNT_LABEL_1",
        "signal_class": "EXEC_MOVEMENT",
        "signal_family": "leadership_change",
        "confidence_score": 0.65,
        "signal_summary": "A senior operating role changed ownership during the last review window.",
        "source_url": "https://placeholder.invalid/events/account-label-1-exec",
    },
    {
        "account_id": "ACCOUNT_LABEL_2",
        "signal_class": "HIRING_SIGNAL",
        "signal_family": "capacity_build",
        "confidence_score": 0.40,
        "signal_summary": "Open role patterns suggest incremental capacity for the affected function.",
        "source_url": "https://placeholder.invalid/events/account-label-2-hiring",
    },
    {
        "account_id": "ACCOUNT_LABEL_3",
        "signal_class": "REGULATORY_FILING",
        "signal_family": "operational_risk",
        "confidence_score": 0.55,
        "signal_summary": "A public filing category indicates new process scrutiny.",
        "source_url": "https://placeholder.invalid/events/account-label-3-filing",
    },
]


PRE_ANNOUNCEMENT = {
    "ACCOUNT_LABEL_1": [],
    "ACCOUNT_LABEL_2": [
        {
            "category": "legacy-incumbent",
            "confidence_score": 0.30,
            "signal_summary": "New placeholder newsroom path appeared during the comparison window.",
        }
    ],
    "ACCOUNT_LABEL_3": [
        {
            "skipped_domain": "placeholder.invalid",
            "reason": "ToS / robots.txt status unclear",
        }
    ],
}


BOARD_CONSTRAINT_SET_A = {
    "min_deal_size": 75000.0,
    "max_cycle_days": 150,
    "required_clone_match": False,
    "min_persona_coverage": 0.25,
}


BOARD_CONSTRAINT_SET_B = {
    "min_deal_size": 120000.0,
    "max_cycle_days": 90,
    "required_clone_match": True,
    "min_persona_coverage": 0.50,
}
