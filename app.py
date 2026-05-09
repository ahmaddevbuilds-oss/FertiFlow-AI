import streamlit as st
import json
import pandas as pd

# =============================================================================
# 1. STATE MANAGEMENT
# =============================================================================
def init_session_state():
    defaults = {
        "country": "Pakistan",
        "micro_region": "Indus Delta",
        "soil_type": "Alluvial (Zarkhaiz)",
        "land_unit": "Killa (Acre)",
        "weight_unit": "Kilogram (kg)",
        "diag_result": None,
        "sched_result": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

# =============================================================================
# 2. STATIC DATA
# =============================================================================
MICRO_REGIONS = {
    "Pakistan": [
        "Indus Delta", "Southern Irrigated Plain", "Sandy Desert",
        "Northern Irrigated Plain", "Barani (Rainfed) Lands", "Wet Mountains",
        "Northern Dry Mountains", "Western Dry Mountains", "Dry Western Plateau",
        "Sulaiman Piedmont"
    ],
    "India": [
        "Western Himalayan", "Eastern Himalayan", "Lower Gangetic Plains",
        "Middle Gangetic Plains", "Upper Gangetic Plains", "Trans-Gangetic Plains",
        "Eastern Plateau & Hills", "Central Plateau & Hills", "Western Plateau & Hills",
        "Southern Plateau & Hills", "East Coast Plains", "West Coast Plains",
        "Gujarat Plains", "Western Dry Region"
    ],
    "Bangladesh": [
        "Himalayan Piedmont Plain", "Tista/Meander Floodplain", "Ganges Tidal Floodplain",
        "Meghna Estuarine Floodplain", "Barind/Madhupur Tracts", "Chittagong Coastal Plain",
        "Northern & Eastern Hills"
    ]
}

SOIL_TYPES = [
    "Alluvial (Zarkhaiz)", "Black (Regur)", "Red Soil", "Laterite",
    "Desert/Arid", "Mountain/Forest", "Saline/Alkaline (Kallar)", "Peaty/Marshy"
]

FERTILIZER_REFERENCE = pd.DataFrame([
    {"🧪 Name": "Urea",          "Main Nutrient": "N (46%)",   "Bag Weight": "50 kg", "Typical Use": "Vegetative growth, tillering"},
    {"🧪 Name": "DAP",           "Main Nutrient": "P + N",     "Bag Weight": "50 kg", "Typical Use": "Basal/rooting, seed germination"},
    {"🧪 Name": "SOP",           "Main Nutrient": "K (50%)",   "Bag Weight": "50 kg", "Typical Use": "Flowering, fruit quality"},
    {"🧪 Name": "MOP",           "Main Nutrient": "K (60%)",   "Bag Weight": "50 kg", "Typical Use": "Flowering, stress resistance"},
    {"🧪 Name": "CAN",           "Main Nutrient": "N + Ca",    "Bag Weight": "50 kg", "Typical Use": "Soil-safe N, alkaline soils"},
    {"🧪 Name": "Zinc Sulphate", "Main Nutrient": "Zn (33%)",  "Bag Weight": "25 kg", "Typical Use": "Micronutrient correction, Kharif crops"},
])

# =============================================================================
# 3. UNIT CONVERSION ENGINE
# =============================================================================
# Base: 1 Acre (Killa) for land, 1 kg for weight
AgriUnits = {
    "land": {
        "Killa (Acre)":     1.0,
        "Kanal":            8.0,
        "Bigha (Standard)": 1.6,
        "Hectare":          0.4047
    },
    "weight": {
        "Kilogram (kg)": 1.0,
        "Maund (Mann)":  0.025,
        "Bag (50kg)":    0.02
    }
}

def calculate_localized_dose(raw_kg_per_acre: float) -> str:
    """
    Converts a raw fertilizer dose (in kg/Acre) to the user's preferred 
    land and weight units selected in the sidebar.
    """
    land_unit   = st.session_state.land_unit
    weight_unit = st.session_state.weight_unit
    land_mult   = AgriUnits["land"][land_unit]
    weight_mult = AgriUnits["weight"][weight_unit]
    converted   = (raw_kg_per_acre / land_mult) * weight_mult
    return f"{converted:.2f} {weight_unit} per {land_unit}"

# =============================================================================
# 4. LLM API LAYER
# =============================================================================
def call_llm_api(prompt: str, system_message: str) -> str:
    """
    Simulates a call to an LLM provider. In a production environment, 
    this would be replaced with actual API requests to Groq, Gemini, or OpenAI.
    """
    api_key = st.secrets.get("API_KEY")
    # Simulating LLM JSON response based on the system_message type
    if "Subcontinent Agronomist" in system_message:
        return '{"diagnosis": "Nitrogen Deficiency", "confidence": "High", "explanation": "Overall yellowing of older leaves and stunted growth typically indicate nitrogen deficiency.", "recommended_fertilizer": "Urea", "raw_dose_kg_per_acre": 25.0}'
    elif "Subcontinent Soil Scientist" in system_message:
        return '{"crop_stage_analysis": "Basal application requires balanced NPK to establish strong roots.", "recommended_fertilizer_1": "DAP", "raw_dose_1_kg_per_acre": 50.0, "recommended_fertilizer_2": "MOP", "raw_dose_2_kg_per_acre": 25.0}'
    return "{}"


def get_diagnostic_recommendation(payload: dict) -> dict:
    """
    Sends diagnostic data to the AI and parses the nutrient deficiency 
    recommendation from the resulting JSON.
    """
    system_message = (
        "You are an expert Subcontinent Agronomist. Analyze the user's crop, region, soil, and visual "
        "symptoms to diagnose the nutrient deficiency or disease. You MUST respond in pure JSON format "
        "with no markdown formatting or extra text. Use this exact schema:\n"
        "{'diagnosis': 'Short name of deficiency/issue',\n"
        " 'confidence': 'High/Medium/Low',\n"
        " 'explanation': '1-sentence explanation',\n"
        " 'recommended_fertilizer': 'Local name e.g., Urea, DAP, SOP, or Zinc Sulphate',\n"
        " 'raw_dose_kg_per_acre': <numeric float>}"
    )
    try:
        return json.loads(call_llm_api(json.dumps(payload), system_message))
    except json.JSONDecodeError:
        return {
            "diagnosis": "Parse Error",
            "confidence": "Low",
            "explanation": "The AI returned an unparseable response. Please try again.",
            "recommended_fertilizer": "Unknown",
            "raw_dose_kg_per_acre": 0.0
        }


def get_schedule_recommendation(payload: dict) -> dict:
    """
    Sends crop and field data to the AI and parses the seasonal 
    fertilizer application schedule from the resulting JSON.
    """
    system_message = (
        "You are an expert Subcontinent Soil Scientist. Based on the crop, target yield, soil type, "
        "previous crop, and region, create a fertilizer application recommendation for the CURRENT growth "
        "stage. You MUST respond in pure JSON format with no markdown formatting. Use this exact schema:\n"
        "{'crop_stage_analysis': '1-sentence agronomic reason',\n"
        " 'recommended_fertilizer_1': 'e.g. Urea/DAP',\n"
        " 'raw_dose_1_kg_per_acre': <numeric float>,\n"
        " 'recommended_fertilizer_2': 'e.g. MOP/Zinc or null',\n"
        " 'raw_dose_2_kg_per_acre': <numeric float or 0>}"
    )
    try:
        return json.loads(call_llm_api(json.dumps(payload), system_message))
    except json.JSONDecodeError:
        return {
            "crop_stage_analysis": "The AI returned an unparseable response.",
            "recommended_fertilizer_1": "Unknown",
            "raw_dose_1_kg_per_acre": 0.0,
            "recommended_fertilizer_2": None,
            "raw_dose_2_kg_per_acre": 0.0
        }

# =============================================================================
# 5. SHARED UI COMPONENTS
# =============================================================================
def render_fertilizer_reference():
    with st.expander("ℹ️ Common Fertilizer Reference Table"):
        st.caption("Quick reference for locally available fertilizers across the Subcontinent.")
        st.dataframe(
            FERTILIZER_REFERENCE,
            use_container_width=True,
            hide_index=True
        )

def render_localization_footer():
    st.markdown("---")
    st.caption(
        f"📍 Advice optimized for the **{st.session_state.micro_region}** "
        f"agro-ecological zone · **{st.session_state.country}** · "
        f"Soil: {st.session_state.soil_type}"
    )

# =============================================================================
# 6. MAIN APP
# =============================================================================
def main():
    # ── Security Check ─────────────────────────────────────────────────────────
    if "API_KEY" not in st.secrets:
        st.error("🔑 **API Key Missing**: Please configure `API_KEY` in Streamlit secrets.")
        st.info("Check `secrets.toml.example` for the required structure.")
        st.stop()

    st.set_page_config(
        page_title="SubcontiFert — Fertilizer Advisor",
        page_icon="🌱",
        layout="wide"
    )
    init_session_state()

    # ── Sidebar ────────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("## 🌱 SubcontiFert")
        st.caption("Fertilizer Advisor for Pakistan · India · Bangladesh")
        st.divider()

        st.header("📍 Regional Settings")
        country = st.selectbox("Country", ["Pakistan", "India", "Bangladesh"], key="country")

        available_regions = MICRO_REGIONS[country]
        if st.session_state.micro_region not in available_regions:
            st.session_state.micro_region = available_regions[0]
        st.selectbox("Agro-Ecological Zone", available_regions, key="micro_region")

        st.header("🪨 Soil Characteristics")
        st.selectbox("Soil Type", SOIL_TYPES, key="soil_type")

        st.header("⚖️ Unit Preferences")
        st.selectbox("Land Unit",   list(AgriUnits["land"].keys()),   key="land_unit")
        st.selectbox("Weight Unit", list(AgriUnits["weight"].keys()), key="weight_unit")

        st.divider()
        st.info(
            f"**Active Profile**\n\n"
            f"🌍 {st.session_state.country}\n\n"
            f"📍 {st.session_state.micro_region}\n\n"
            f"🪨 {st.session_state.soil_type}"
        )
        st.divider()
        st.caption(
            "⚠️ **Disclaimer**: This is an AI-powered demonstration tool. "
            "Agricultural conditions vary wildly. Always verify AI-generated "
            "recommendations with a local soil test and a certified agronomist "
            "before applying chemical fertilizers."
        )

    # ── Page Header ────────────────────────────────────────────────────────────
    st.title("🌱 Subcontinent Fertilizer Advisor")
    st.markdown(
        f"Personalized fertilizer guidance for the **{st.session_state.micro_region}** region "
        f"(**{st.session_state.country}**) · Soil: {st.session_state.soil_type} · "
        f"Units: {st.session_state.weight_unit} / {st.session_state.land_unit}"
    )
    st.divider()

    # ── Tabs ───────────────────────────────────────────────────────────────────
    tab1, tab2 = st.tabs(["🩺 Plant Doctor (Diagnostics)", "🌾 Preventative Plan (Yield Optimizer)"])

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 — Symptom-Based Diagnostics
    # ══════════════════════════════════════════════════════════════════════════
    with tab1:
        st.subheader("🩺 Symptom-Based Nutrient Diagnostic")
        st.caption(
            "Describe what you observe in the field. The tool cross-references your symptoms "
            "with known nutrient deficiency patterns for your region and soil type."
        )

        with st.container(border=True):
            with st.form(key="diagnostic_form"):
                col1, col2 = st.columns(2)
                with col1:
                    target_crop = st.selectbox(
                        "🌿 Target Crop",
                        ["Wheat", "Rice", "Cotton", "Sugarcane", "Maize", "Tomato", "Potato"],
                        help="Select the crop currently being grown."
                    )
                    soil_moisture = st.select_slider(
                        "💧 Soil Moisture Condition",
                        options=["Very Dry", "Normal/Moist", "Waterlogged/Muddy"],
                        value="Normal/Moist",
                        help="Waterlogging can mimic N deficiency even when N is present."
                    )

                with col2:
                    affected_area = st.radio(
                        "📍 Affected Area (Location on Plant)",
                        ["Lower/Older Leaves", "Upper/Newer Leaves", "Whole Plant", "Fruit/Flower"],
                        help="Mobile nutrients (N, P, K, Mg) → older leaves. Immobile (Fe, Ca, B) → newer leaves."
                    )

                st.divider()
                visual_symptoms = st.multiselect(
                    "👁️ Visual Symptoms (select all that apply)",
                    [
                        "Overall Yellowing (Chlorosis)",
                        "Yellowing between veins",
                        "Browning/Burnt edges (Necrosis)",
                        "Purple tints on undersides",
                        "Stunted growth",
                        "Leaf curling"
                    ],
                    help="Select every visible symptom."
                )
                st.form_submit_button("🔬 Analyze Symptoms", use_container_width=True, type="primary")

        # Trigger detection: re-check submitted state via button press detection
        submitted = st.session_state.get("diagnostic_form_submitted", False)

        # Use a workaround: check if visual_symptoms changed via a dedicated submit button
        # Post-submission results area
        with st.container(border=True):
            st.markdown("#### 📋 Diagnostic Results")

            if not visual_symptoms:
                st.info("ℹ️ Fill out the form above and click **Analyze Symptoms** to see your personalized diagnosis.")
            else:
                # Form was interacted with — run analysis on submit
                with st.spinner("🔬 Consulting the Soil Database..."):
                    diagnostic_payload = {
                        "target_crop": target_crop,
                        "affected_area": affected_area,
                        "visual_symptoms": visual_symptoms,
                        "soil_moisture": soil_moisture,
                        "country": st.session_state.country,
                        "micro_region": st.session_state.micro_region,
                        "soil_type": st.session_state.soil_type,
                        "land_unit": st.session_state.land_unit,
                        "weight_unit": st.session_state.weight_unit
                    }
                    diag = get_diagnostic_recommendation(diagnostic_payload)

                diagnosis   = diag.get("diagnosis", "Unknown")
                confidence  = diag.get("confidence", "Low")
                explanation = diag.get("explanation", "No explanation provided.")
                rec_fert    = diag.get("recommended_fertilizer", "Unknown")
                raw_dose    = float(diag.get("raw_dose_kg_per_acre") or 0.0)

                # Confidence-based alert level
                if confidence == "High":
                    st.error(f"🩺 **Diagnosis ({confidence} confidence):** {diagnosis}")
                elif confidence == "Medium":
                    st.warning(f"🩺 **Diagnosis ({confidence} confidence):** {diagnosis}")
                else:
                    st.info(f"🩺 **Diagnosis ({confidence} confidence):** {diagnosis}")

                st.warning(f"💬 **Explanation:** {explanation}")

                if raw_dose > 0:
                    converted_dose = calculate_localized_dose(raw_dose)
                    st.success(f"🛠️ **Action Required:** Apply **{converted_dose}** of 🧪 **{rec_fert}**.")
                else:
                    st.success(f"🛠️ **Action Required:** Consider applying 🧪 **{rec_fert}** — dose to be determined by soil test.")

        render_fertilizer_reference()
        render_localization_footer()

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2 — Preventative Plan (Yield Optimizer)
    # ══════════════════════════════════════════════════════════════════════════
    with tab2:
        st.subheader("🌾 Preventative Fertilizer Plan")
        st.caption(
            "Plan your fertilizer schedule ahead of the season. Inputs are tailored to your "
            "region, soil type, and local unit preferences set in the sidebar."
        )

        with st.container(border=True):
            with st.form(key="recommendation_form"):
                col1, col2 = st.columns(2)
                with col1:
                    rec_crop = st.selectbox(
                        "🌿 Target Crop",
                        ["Wheat", "Rice", "Cotton", "Sugarcane", "Maize", "Potato"],
                        help="Select the crop you intend to grow this season."
                    )
                    growth_stage = st.select_slider(
                        "🌱 Current Growth Stage",
                        options=["Pre-Planting/Basal", "Seedling", "Vegetative Growth",
                                 "Flowering/Reproductive", "Fruiting/Grain Filling"],
                        value="Pre-Planting/Basal",
                        help="Select the stage at which you want to apply fertilizer."
                    )

                with col2:
                    target_yield = st.number_input(
                        f"🎯 Expected Target Yield ({st.session_state.weight_unit} per {st.session_state.land_unit})",
                        min_value=0.0, value=40.0, step=5.0,
                        help="Higher yield targets require proportionally more fertilizer input."
                    )
                    prev_crop = st.selectbox(
                        "🔄 Previous Crop History",
                        ["Legume/Pulses", "Cereal/Grain", "Fallow/Empty", "Other"],
                        help="Legumes fix atmospheric N — this may reduce your required N dose."
                    )

                st.divider()
                irrigation_source = st.radio(
                    "💦 Irrigation Source",
                    ["Canal Water", "Tube-well/Groundwater", "Rainfed/Barani"],
                    horizontal=True,
                    help="Tube-well water can raise soil salinity over time, reducing nutrient uptake."
                )

                rec_submitted = st.form_submit_button(
                    "📋 Generate Fertilizer Schedule",
                    use_container_width=True,
                    type="primary"
                )

        # ── Results ────────────────────────────────────────────────────────────
        with st.container(border=True):
            st.markdown("#### 📋 Fertilizer Schedule")

            if not rec_submitted:
                st.info("ℹ️ Fill out the form above and click **Generate Fertilizer Schedule** to see your personalized recommendation.")
            else:
                with st.spinner("🌾 Consulting the Soil Database..."):
                    schedule_payload = {
                        "target_crop": rec_crop,
                        "target_yield": target_yield,
                        "yield_unit": f"{st.session_state.weight_unit} per {st.session_state.land_unit}",
                        "growth_stage": growth_stage,
                        "previous_crop": prev_crop,
                        "irrigation_source": irrigation_source,
                        "country": st.session_state.country,
                        "micro_region": st.session_state.micro_region,
                        "soil_type": st.session_state.soil_type,
                        "land_unit": st.session_state.land_unit,
                        "weight_unit": st.session_state.weight_unit
                    }
                    sched = get_schedule_recommendation(schedule_payload)

                analysis  = sched.get("crop_stage_analysis", "No analysis provided.")
                fert_1    = sched.get("recommended_fertilizer_1", "Unknown")
                raw_1     = float(sched.get("raw_dose_1_kg_per_acre") or 0.0)
                fert_2    = sched.get("recommended_fertilizer_2")
                raw_2     = float(sched.get("raw_dose_2_kg_per_acre") or 0.0)

                st.info(f"💡 **Agronomic Insight:** {analysis}")

                if raw_1 > 0:
                    st.success(
                        f"🌾 **Fertilizer 1:** Apply **{calculate_localized_dose(raw_1)}** "
                        f"of 🧪 **{fert_1}**"
                    )
                if raw_2 > 0 and fert_2 and str(fert_2).lower() not in ["none", "null"]:
                    st.success(
                        f"🌾 **Fertilizer 2:** Apply **{calculate_localized_dose(raw_2)}** "
                        f"of 🧪 **{fert_2}**"
                    )

        render_fertilizer_reference()
        render_localization_footer()


if __name__ == "__main__":
    main()
