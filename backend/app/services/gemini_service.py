"""AgroAI Gemini-Powered Agronomic Copilot Service.

Communicates with Google Gemini API securely on the backend.
The GEMINI_API_KEY is never exposed to clients or frontend code.
Supports configurable model selection (GEMINI_MODEL) and provides
an expert agricultural heuristic fallback if offline or unkeyed.
"""

import os
import json
import urllib.request
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv, dotenv_values

# Load environment variables from backend/.env
ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")
if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)

def _get_gemini_config():
    """Retrieve GEMINI_API_KEY and GEMINI_MODEL from .env or system environment."""
    env_vals = dotenv_values(ENV_PATH) if os.path.exists(ENV_PATH) else {}
    api_key = (env_vals.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY") or "").strip()
    model_name = (env_vals.get("GEMINI_MODEL") or os.environ.get("GEMINI_MODEL") or "gemini-3.5-flash-lite").strip() or "gemini-3.5-flash-lite"
    return api_key, model_name

SYSTEM_INSTRUCTION = """You are AgroAI Copilot, an elite agricultural AI specialist and crop pathologist.
Your role is to assist farmers, agronomists, and growers with practical, science-based guidance on:
1. Plant pathology identification and treatment (fungal, bacterial, viral).
2. Soil fertility, organic composting, and balanced NPK fertilizer management.
3. Micro-irrigation scheduling and evapotranspiration management.
4. Integrated Pest Management (IPM) prioritizing biological and preventative controls.

Tone & Style:
- Professional, supportive, and practical.
- Use clear bullet points and bold section headers.
- Always include organic remedies alongside approved agronomic practices.
- State clearly that high-potency chemical pesticides should be applied per local agricultural extension (e.g. KVK / ICAR) instructions.
"""

# Expert offline knowledge catalog for guaranteed uptime
OFFLINE_KNOWLEDGE = {
    "early blight": (
        "### Early Blight (*Alternaria solani*) Treatment Protocol\n\n"
        "**Immediate Agronomic Actions:**\n"
        "- **Pruning:** Remove and safely discard all infected lower foliage exhibiting concentric 'target-board' spots.\n"
        "- **Irrigation Adjustment:** Transition immediately to drip irrigation. Avoid overhead sprinklers that wet foliage for extended hours.\n"
        "- **Mulching:** Lay a 2-3 inch organic straw or plastic mulch barrier to stop soil-borne fungal spores from splashing onto leaves.\n\n"
        "**Treatment Options:**\n"
        "- *Organic/Biological:* Spray *Bacillus subtilis* or neem oil formulation (5ml/L) at 7-day intervals.\n"
        "- *Standard Protective:* Apply copper oxychloride (2.5g/L) or Mancozeb before lesions reach the upper fruit canopy."
    ),
    "late blight": (
        "### Late Blight (*Phytophthora infestans*) Emergency Protocol\n\n"
        "**Urgent Alert:** Late blight spreads aggressively during cool, humid weather (>85% RH, 15-22°C).\n\n"
        "- **Quarantine:** Immediately isolate infected sectors. Remove blighted plants showing dark water-soaked rot.\n"
        "- **Airflow:** Increase canopy ventilation and thin out dense foliage.\n"
        "- **Treatment:** Apply approved systemic and contact protectants (e.g., Cymoxanil + Mancozeb, or copper hydroxide). Avoid working in fields while leaves are wet."
    ),
    "brown spot": (
        "### Rice Brown Spot (*Bipolaris oryzae*) Management\n\n"
        "**Root Causes:** Brown spot commonly thrives in soils deficient in potassium, silicon, or organic matter, especially under water-deficit stress.\n\n"
        "**Recovery Actions:**\n"
        "- **Water Level:** Maintain a continuous 3-5 cm standing water layer in the paddy during tillering and panicle initiation.\n"
        "- **Nutrition:** Top-dress with Muriate of Potash (MOP) and well-decomposed organic manure to correct nutrient stress.\n"
        "- **Foliar Intervention:** Apply Propiconazole (1ml/L) or Tricyclazole if lesions expand onto the flag leaf."
    ),
    "fertilizer": (
        "### Balanced NPK Soil Nutrition Guidelines\n\n"
        "- **Basal Application:** Incorporate full Phosphorus (DAP/SSP) and 50% Potassium (MOP) into the soil bed prior to transplanting.\n"
        "- **Nitrogen Split:** Split Nitrogen (Urea) into 3 equal doses: 1/3 at basal, 1/3 at active tillering/vegetative, and 1/3 at flower bud initiation.\n"
        "- **Organic Health:** Apply 5-8 tonnes/hectare of well-composted farmyard manure (FYM) or vermicompost to enhance cation exchange capacity (CEC)."
    ),
    "irrigation": (
        "### Precision Irrigation Recommendations\n\n"
        "- **Target Soil Moisture:** Maintain 40-50% field capacity for Solanaceae crops (Tomato, Potato).\n"
        "- **Drip Efficiency:** Drip systems deliver 90%+ water-use efficiency compared to 55-65% in flood basins.\n"
        "- **Timing:** Run irrigation in the early morning (05:30 - 08:30 AM) to minimize evaporative loss and allow foliage to dry before nightfall."
    )
}

class GeminiService:
    @staticmethod
    def is_configured() -> bool:
        """Check whether a valid GEMINI_API_KEY is configured."""
        api_key, _ = _get_gemini_config()
        return bool(api_key and api_key != "YOUR_GEMINI_API_KEY_HERE")

    @staticmethod
    def ask_copilot(
        prompt: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        crop_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process farmer inquiries using Gemini API or report not configured."""
        api_key, model_name = _get_gemini_config()

        # If key is missing or placeholder, clearly report not configured
        if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
            unconfigured_msg = (
                "Gemini API key is not configured. "
                "To enable live Google Gemini generative responses, set the GEMINI_API_KEY environment variable in backend/.env. "
                f"(Target model: {model_name})"
            )
            return {
                "reply": unconfigured_msg,
                "response": unconfigured_msg,
                "model": model_name,
                "provider": "Gemini (Not Configured)",
                "status": "not_configured"
            }

        # If a valid API key exists, call Google Gemini REST API using header authentication
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
            
            contents = []
            full_user_prompt = prompt
            if crop_context:
                full_user_prompt = f"[Context: Farmer has selected crop scan '{crop_context}']\n\n{prompt}"

            if chat_history:
                for msg in chat_history[-6:]:
                    role = "user" if msg.get("sender") == "user" else "model"
                    contents.append({"role": role, "parts": [{"text": msg.get("text", "")}]})

            contents.append({"role": "user", "parts": [{"text": full_user_prompt}]})

            payload = {
                "contents": contents,
                "systemInstruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
                "generationConfig": {
                    "temperature": 0.4,
                    "maxOutputTokens": 1024
                }
            }

            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "x-goog-api-key": api_key
                }
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            candidates = data.get("candidates", [])
            if candidates and "content" in candidates[0] and "parts" in candidates[0]["content"]:
                reply_text = candidates[0]["content"]["parts"][0].get("text", "")
                return {
                    "reply": reply_text,
                    "response": reply_text,
                    "model": model_name,
                    "provider": "Google Gemini API",
                    "status": "online"
                }
            else:
                return {
                    "reply": "No response text returned from Gemini API.",
                    "response": "No response text returned from Gemini API.",
                    "model": model_name,
                    "provider": "Google Gemini API",
                    "status": "empty_response"
                }

        except urllib.error.HTTPError as e:
            try:
                err_body = e.read().decode("utf-8")
                err_json = json.loads(err_body)
                api_msg = err_json.get("error", {}).get("message", err_body)
            except Exception:
                api_msg = str(e)
            if api_key:
                api_msg = api_msg.replace(api_key, "[REDACTED]")
            error_msg = f"Gemini API error: {api_msg}"
            return {
                "reply": error_msg,
                "response": error_msg,
                "model": model_name,
                "provider": "Google Gemini API",
                "status": "error"
            }
        except Exception as e:
            err_str = str(e)
            if api_key:
                err_str = err_str.replace(api_key, "[REDACTED]")
            error_msg = f"Gemini API connection error: {err_str}"
            return {
                "reply": error_msg,
                "response": error_msg,
                "model": model_name,
                "provider": "Google Gemini API",
                "status": "error"
            }
