"""
Unit and Integration tests for the Accessibility Intelligence Layer.
"""
import pytest
from app.intelligence.blink_command_processor import BlinkCommandProcessor
from app.intelligence.eye_command_processor import EyeCommandProcessor
from app.intelligence.gesture_command_processor import GestureCommandProcessor
from app.intelligence.context_engine import ContextEngine
from app.intelligence.phrase_predictor import PhrasePredictor
from app.intelligence.user_behavior import UserBehaviorManager
from app.intelligence.history_manager import HistoryManager
from app.intelligence.rules_engine import RulesEngine
from app.intelligence.intent_engine import IntentEngine
from app.intelligence.accessibility_engine import AccessibilityEngine


# --- Unit Tests: BlinkCommandProcessor ---

def test_blink_processor_single_blink():
    processor = BlinkCommandProcessor()
    res = processor.process_blink(blink_type="single", duration_ms=200)
    assert res["intent"] == "SELECT"
    assert res["command"] == "SELECT_ITEM"
    assert res["detected_type"] == "single_blink"


def test_blink_processor_double_blink():
    processor = BlinkCommandProcessor()
    res = processor.process_blink(blink_type="double", count=2, duration_ms=150)
    assert res["intent"] == "CONFIRM"
    assert res["command"] == "CONFIRM_ACTION"


def test_blink_processor_long_blink():
    processor = BlinkCommandProcessor()
    res = processor.process_blink(duration_ms=600)
    assert res["intent"] == "OPEN_MENU"
    assert res["command"] == "TOGGLE_MENU"


def test_blink_processor_sequence():
    processor = BlinkCommandProcessor()
    res = processor.process_blink(sequence=["short", "long", "short"])
    assert res["intent"] == "BLINK_SEQUENCE"
    assert res["command"] == "EXECUTE_SEQUENCE"


# --- Unit Tests: EyeCommandProcessor ---

def test_eye_processor_gaze_direction():
    processor = EyeCommandProcessor()
    res = processor.process_eye({"gaze_direction": "left", "x": 0.1, "y": 0.5})
    assert res["intent"] == "LOOK_LEFT"
    assert res["command"] == "NAVIGATE_LEFT"
    assert res["zone"] == "MIDDLE_LEFT"


def test_eye_processor_dwell_selection():
    processor = EyeCommandProcessor(dwell_threshold_ms=800.0)
    res = processor.process_eye({"gaze_direction": "center", "x": 0.5, "y": 0.5, "dwell_time_ms": 1000.0})
    assert res["intent"] == "SELECT"
    assert res["command"] == "DWELL_SELECT"


def test_eye_processor_grid_and_zone():
    processor = EyeCommandProcessor(grid_rows=3, grid_cols=3)
    res = processor.process_eye({"x": 0.8, "y": 0.2})
    assert res["zone"] == "TOP_RIGHT"
    assert res["grid_cell"] == "R1C3"


# --- Unit Tests: GestureCommandProcessor ---

def test_gesture_processor_known_gestures():
    processor = GestureCommandProcessor()
    gestures = [
        ("open_palm", "OPEN_MENU"),
        ("closed_fist", "CANCEL"),
        ("thumbs_up", "CONFIRM"),
        ("pointing", "SELECT"),
        ("pinch", "SELECT"),
    ]
    for g_name, expected_intent in gestures:
        res = processor.process_gesture({"name": g_name, "confidence": 0.95})
        assert res["intent"] == expected_intent


def test_gesture_processor_custom_fallback():
    processor = GestureCommandProcessor()
    res = processor.process_gesture({"name": "wave_hand", "confidence": 0.85})
    assert res["intent"] == "CUSTOM_GESTURE"
    assert res["command"] == "ACTION_WAVE_HAND"


# --- Unit Tests: ContextEngine ---

def test_context_engine_updates():
    engine = ContextEngine()
    engine.set_screen("keyboard")
    engine.set_mode("AAC")
    engine.record_command("TYPE_A", "TYPE_CHARACTER")
    engine.update_conversation("Hello world", speaker="user")

    ctx = engine.get_context()
    assert ctx["current_screen"] == "keyboard"
    assert ctx["active_mode"] == "AAC"
    assert len(ctx["last_commands"]) == 1
    assert ctx["conversation_context"]["last_speaker"] == "user"


# --- Unit Tests: PhrasePredictor ---

def test_phrase_predictor_features():
    predictor = PhrasePredictor()
    predictor.add_favorite("Custom Favorite Phrase")
    predictor.pin_phrase("Quick Emergency Phrase")
    predictor.record_phrase_usage("Hello world")

    preds = predictor.get_predictions(prefix="Quick", current_screen="home")
    assert len(preds) > 0
    assert preds[0]["phrase"] == "Quick Emergency Phrase"
    assert preds[0]["source"] == "pinned"


# --- Unit Tests: UserBehavior & HistoryManager ---

def test_user_behavior_management():
    manager = UserBehaviorManager()
    manager.update_profile(eye_sensitivity=1.2, dominant_eye="left", preferred_language="es")
    profile = manager.get_profile()
    assert profile["eye_sensitivity"] == 1.2
    assert profile["dominant_eye"] == "left"
    assert profile["preferred_language"] == "es"


def test_history_manager_logging():
    hm = HistoryManager()
    hm.record_command("SELECT_ITEM", "SELECT")
    hm.record_decision("SOS_TRIGGER", 0.99, "TRIGGER_EMERGENCY_SOS", "Rule match", inputs={})
    hm.record_emergency("rules_engine", "Emergency SOS triggered", payload={})

    cmds = hm.get_history(category="command")
    assert len(cmds) == 1
    assert cmds[0]["intent"] == "SELECT"

    emergencies = hm.get_history(category="emergency")
    assert len(emergencies) == 1
    assert emergencies[0]["trigger_source"] == "rules_engine"


# --- Unit Tests: RulesEngine ---

def test_rules_engine_sos_trigger():
    re = RulesEngine()
    res = re.evaluate_rules(
        eye_data={"gaze_direction": "left"},
        blink_data={"blink_type": "double", "count": 2},
    )
    assert res is not None
    assert res["intent"] == "SOS_TRIGGER"
    assert res["command"] == "TRIGGER_EMERGENCY_SOS"


# --- Integration Tests: IntentEngine & AccessibilityEngine ---

def test_intent_engine_rule_priority():
    ie = IntentEngine()
    res = ie.process_intent(
        eye_tracking={"gaze_direction": "left"},
        blink={"blink_type": "double"},
    )
    assert res["intent"] == "SOS_TRIGGER"
    assert res["confidence"] == 0.99


def test_intent_engine_lip_reading():
    ie = IntentEngine()
    res = ie.process_intent(lip_reading={"detected_text": "delete"})
    assert res["intent"] == "DELETE_CHARACTER"
    assert res["command"] == "ACTION_DELETE"


# --- Integration Tests: FastAPI Endpoints ---

def test_api_process_intelligence_rule(client):
    payload = {
        "eye_tracking": {"gaze_direction": "left"},
        "blink": {"blink_type": "double", "count": 2},
    }
    response = client.post("/intelligence/process", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["intent"] == "SOS_TRIGGER"
    assert data["command"] == "TRIGGER_EMERGENCY_SOS"
    assert data["confidence"] >= 0.95


def test_api_process_intelligence_gaze(client):
    payload = {
        "eye_tracking": {"gaze_direction": "right"},
    }
    response = client.post("/intelligence/process", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["intent"] == "LOOK_RIGHT"


def test_api_calibrate(client):
    payload = {
        "eye_sensitivity": 1.5,
        "blink_sensitivity": 1.2,
        "dominant_eye": "left",
        "preferred_language": "es",
    }
    response = client.post("/intelligence/calibrate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["profile"]["eye_sensitivity"] == 1.5
    assert data["profile"]["dominant_eye"] == "left"


def test_api_history(client):
    response = client.get("/intelligence/history?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "history" in data


def test_api_profile(client):
    response = client.get("/intelligence/profile")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "profile" in data
