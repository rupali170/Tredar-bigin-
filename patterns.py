from PIL import Image
import numpy as np
import random

def extract_vertical_profile(img: Image.Image) -> np.ndarray:
    """
    chart मधील price movement rough समजण्यासाठी vertical brightness profile काढतो.
    assumption: chart background dark, candles/light असतील.
    """
    gray = img.convert("L")
    arr = np.array(gray)
    col_mean = arr.mean(axis=1)  # प्रत्येक row चा mean
    # normalize 0-1
    col_norm = (col_mean - col_mean.min()) / (col_mean.ptp() + 1e-6)
    return col_norm


def detect_trend(profile: np.ndarray) -> str:
    """
    वरचा profile वापरून rough trend type ठरवतो.
    खूप साधा अंदाज: वरच्या rows आणि खालच्या rows मधला फरक.
    """
    n = len(profile)
    top = profile[: n // 3].mean()
    mid = profile[n // 3 : 2 * n // 3].mean()
    bottom = profile[2 * n // 3 :].mean()

    # background dark assumed; brightness जास्त = candles वरती.
    # हे फक्त relative estimate आहे.
    score_up = top - bottom  # positive म्हणजे candles वर जास्त
    score_down = bottom - top

    if abs(score_up) < 0.03:
        return "SIDEWAYS"
    elif score_up > 0:
        return "UP"
    else:
        return "DOWN"


def dummy_pattern_hint(profile: np.ndarray) -> str:
    """
    फक्त काही small नियमांवर आधारित textual hint.
    """
    n = len(profile)
    top = profile[: n // 3].mean()
    bottom = profile[2 * n // 3 :].mean()
    mid = profile[n // 3 : 2 * n // 3].mean()

    text = []

    if mid > top and mid > bottom:
        text.append("मधल्या भागात activity जास्त दिसत आहे.")
    if top > mid and top > bottom:
        text.append("चार्टच्या वरच्या भागात recent move strong वाटतो.")
    if bottom > mid and bottom > top:
        text.append("खालच्या भागात दबाव/सेलिंग दिसू शकते.")

    if abs(top - bottom) < 0.02:
        text.append("एकंदरीत chart फार directional नाही, sideways असू शकतो.")
    return " ".join(text) if text else "Normal volatility दिसते."


def decide_action(trend: str) -> tuple[str, float, str]:
    """
    trend वरून BUY / SELL / WAIT निर्णय.
    हे साधं rule-based engine आहे.
    """
    if trend == "UP":
        action = "BUY"
        confidence = round(random.uniform(55, 70), 1)
        reason = "Trend अंदाजे UP आहे, buyer control मध्ये असू शकतात."
    elif trend == "DOWN":
        action = "SELL"
        confidence = round(random.uniform(55, 70), 1)
        reason = "Trend अंदाजे DOWN आहे, sellers active असू शकतात."
    else:
        action = "WAIT"
        confidence = round(random.uniform(50, 65), 1)
        reason = "Clear direction नाही, त्यामुळे थांबणे किंवा लहान position योग्य."
    return action, confidence, reason


def analyze_chart_image(img: Image.Image) -> dict:
    """
    मुख्य function: image घेऊन profile -> trend -> decision देतो.
    """
    # image थोडा resize करून process कमी करा
    img_small = img.resize((img.width // 2, img.height // 2))

    profile = extract_vertical_profile(img_small)
    trend = detect_trend(profile)
    pattern_hint = dummy_pattern_hint(profile)
    action, confidence, reason = decide_action(trend)

    full_reason = f"{reason} {pattern_hint} (हे फक्त demo analysis आहे.)"

    return {
        "trend": trend,
        "action": action,
        "confidence": confidence,
        "reason": full_reason,
    }
