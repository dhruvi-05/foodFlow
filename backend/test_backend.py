"""
Backend Endpoints Test Suite for WasteWise AI.
Tests all 6 API handlers locally.
"""

import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.fn_plan.app import plan_handler
from backend.fn_explain.app import explain_handler, ask_handler
from backend.fn_waste.app import waste_handler
from backend.fn_simulate.app import simulate_handler
from backend.fn_ingest.app import upload_url_handler


def test_all_endpoints():
    print("=" * 60)
    print("RUNNING BACKEND API ENDPOINTS TEST SUITE")
    print("=" * 60)

    # 1. GET /api/plan
    event_plan = {"queryStringParameters": {"restaurant_id": "R001", "date": "2026-09-19"}}
    res_plan = plan_handler(event_plan)
    assert res_plan["statusCode"] == 200, f"GET /api/plan failed: {res_plan}"
    body_plan = json.loads(res_plan["body"])
    assert "items" in body_plan and len(body_plan["items"]) == 5, "Plan item count mismatch"
    assert "totals" in body_plan and "purchase_list" in body_plan
    print(f"✅ 1. GET /api/plan passed. Generated {len(body_plan['items'])} dish cards. Expected Revenue: ₹{body_plan['totals']['expected_revenue']:,}")

    # 2. POST /api/explain
    sample_item = body_plan["items"][0]
    event_explain = {"body": json.dumps({"item": sample_item})}
    res_explain = explain_handler(event_explain)
    assert res_explain["statusCode"] == 200, f"POST /api/explain failed: {res_explain}"
    body_explain = json.loads(res_explain["body"])
    assert "explanation" in body_explain and body_explain["grounded"] is True
    print(f"✅ 2. POST /api/explain passed. Grounded explanation: '{body_explain['explanation'][:80]}...'")

    # 3. POST /api/ask
    event_ask = {"body": json.dumps({"question": "Why should I prepare fewer dal portions tomorrow?", "context": body_plan})}
    res_ask = ask_handler(event_ask)
    assert res_ask["statusCode"] == 200, f"POST /api/ask failed: {res_ask}"
    body_ask = json.loads(res_ask["body"])
    assert "answer" in body_ask
    print(f"✅ 3. POST /api/ask passed. Answer: '{body_ask['answer'][:80]}...'")

    # 4. GET /api/waste
    res_waste = waste_handler({})
    assert res_waste["statusCode"] == 200, f"GET /api/waste failed: {res_waste}"
    body_waste = json.loads(res_waste["body"])
    assert "weekly_waste_value" in body_waste and "dish_breakdown" in body_waste
    print(f"✅ 4. GET /api/waste passed. Weekly Waste: ₹{body_waste['weekly_waste_value']:,} ({body_waste['wow_delta_pct']}% WoW). Insight: '{body_waste['insight_sentence']}'")

    # 5. POST /api/simulate
    res_sim = simulate_handler({})
    assert res_sim["statusCode"] == 200, f"POST /api/simulate failed: {res_sim}"
    body_sim = json.loads(res_sim["body"])
    assert "headline_saving_rupees" in body_sim and len(body_sim["metrics"]) == 6
    print(f"✅ 5. POST /api/simulate passed. Net 30-Day Benefit: ₹{body_sim['headline_saving_rupees']:,} ({body_sim['waste_cost_reduction_pct']}% waste cost reduction)")

    # 6. POST /api/upload-url
    res_upload = upload_url_handler({})
    assert res_upload["statusCode"] == 200, f"POST /api/upload-url failed: {res_upload}"
    body_upload = json.loads(res_upload["body"])
    assert "upload_url" in body_upload
    print(f"✅ 6. POST /api/upload-url passed. Presigned URL generated: {body_upload['upload_url'][:45]}...")

    print("\n🎉 ALL 6 BACKEND ENDPOINT TESTS PASSED CLEANLY!")


if __name__ == "__main__":
    test_all_endpoints()
