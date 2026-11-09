"""Training content for PV Case Lab.

Everything in this file is FICTIONAL: patients, reporters, products and documents.
To add a case, copy one block inside CASES and edit the text. No other code changes
are needed, because the app reads all cases from this list.
"""

PRODUCTS = {
    "Cardiolux 10 mg": {
        "document": "Fictional SmPC, section 4.8 Undesirable effects",
        "version": "v3.2",
        "country": "EU (centralised)",
        "effective": "01 March 2026",
        "reactions": [
            ("Headache", "Common"),
            ("Dizziness", "Common"),
            ("Nausea", "Uncommon"),
            ("Skin rash", "Uncommon"),
            ("Peripheral oedema", "Rare"),
        ],
    },
    "Fluvanta 200 mg": {
        "document": "Fictional SmPC, section 4.8 Undesirable effects",
        "version": "v2.0",
        "country": "EU (national, Bulgaria)",
        "effective": "15 January 2026",
        "reactions": [
            ("Nausea", "Common"),
            ("Abdominal pain", "Common"),
            ("Elevated liver enzymes", "Common"),
            ("Skin rash", "Uncommon"),
            ("Hepatitis", "Rare"),
        ],
    },
}

# Reporting rules are DATA, not hard-coded numbers. Version 1 covers the EU
# post-marketing pathway completely; the other rows exist so learners can see
# that different regulatory pathways are not interchangeable.
RULES = [
    {"id": "EU-PM-SER", "name": "EU post-marketing: serious ICSR (marketing authorisation holder)",
     "days": 15, "serious": True, "framework": "EU post-marketing",
     "source": "EU pharmacovigilance legislation and GVP Module VI", "version": "training 1.0"},
    {"id": "EU-PM-NONSER", "name": "EU post-marketing: non-serious ICSR from the EEA",
     "days": 90, "serious": False, "framework": "EU post-marketing",
     "source": "EU pharmacovigilance legislation and GVP Module VI", "version": "training 1.0"},
    {"id": "EU-CT-FATAL", "name": "EU clinical trial: fatal or life-threatening SUSAR",
     "days": 7, "serious": True, "framework": "EU clinical trials",
     "source": "Regulation (EU) No 536/2014", "version": "contrast only"},
    {"id": "EU-CT-OTHER", "name": "EU clinical trial: other SUSAR",
     "days": 15, "serious": True, "framework": "EU clinical trials",
     "source": "Regulation (EU) No 536/2014", "version": "contrast only"},
    {"id": "US-PM-15D", "name": "US post-marketing: serious and unexpected (15-day alert)",
     "days": 15, "serious": True, "framework": "US post-marketing",
     "source": "21 CFR 314.80", "version": "contrast only"},
    {"id": "US-IND-FATAL", "name": "US IND: unexpected fatal or life-threatening suspected reaction",
     "days": 7, "serious": True, "framework": "US clinical trials",
     "source": "FDA IND safety reporting rules", "version": "contrast only"},
]

STAGES = [
    ("validity", "Validity and follow-up", 15),
    ("coding", "Event coding", 10),
    ("seriousness", "Seriousness", 15),
    ("causality", "Causality", 15),
    ("expectedness", "Expectedness", 15),
    ("timeline", "Reporting timeline", 20),
    ("narrative", "Narrative and QC", 10),
]

ELEMENTS = [
    ("patient", "Identifiable patient"),
    ("reporter", "Identifiable reporter"),
    ("product", "Suspect medicinal product"),
    ("event", "Adverse event"),
]

CRITERIA = [
    ("death", "Death", "Did the event result in the patient's death?"),
    ("life", "Life-threatening", "Was the patient at immediate risk of death when the event occurred?"),
    ("hosp", "Hospitalisation", "Did it need inpatient admission or prolong a hospital stay?"),
    ("disab", "Disability or incapacity", "Persistent or significant disability or incapacity?"),
    ("congen", "Congenital anomaly", "Congenital anomaly or birth defect?"),
    ("mie", "Other medically important event", "Could it jeopardise the patient or need intervention to prevent a serious outcome?"),
]

NJ_Q = [
    "Are there previous conclusive reports of this reaction?",
    "Did the event appear after the suspect drug was given?",
    "Did the reaction improve when the drug was stopped (or an antagonist given)?",
    "Did the reaction reappear when the drug was given again?",
    "Are there alternative causes that could on their own have caused the reaction?",
    "Did the reaction reappear when a placebo was given?",
    "Was the drug detected in blood at toxic concentrations?",
    "Was the reaction more severe at a higher dose or less severe at a lower dose?",
    "Did the patient have a similar reaction to the same or similar drug before?",
    "Was the event confirmed by objective evidence?",
]
# Points for Yes / No (Don't know is always 0)
NJ_PTS = [(1, 0), (2, -1), (1, 0), (2, -1), (-1, 2), (-1, 1), (1, 0), (1, 0), (1, 0), (1, 0)]

WHO_CLASSES = ["Certain", "Probable/Likely", "Possible", "Unlikely",
               "Conditional/Unclassified", "Unassessable/Unclassifiable"]

CODING_RULES = [
    "Always code the most severe diagnosis that could explain the event",
    "Code what the reporter said and do not add an unsupported diagnosis",
    "Code the known side effect from the product information instead of the reported event",
]

EXP_CHOICES = ["Expected", "Unexpected", "Cannot be determined from the information available"]

HINTS = {
    "validity": "Four minimum elements are needed. An age or sex can identify a patient; a username alone does not prove a real patient or reporter exists.",
    "coding": "Code what was reported. Do not turn symptoms into a diagnosis nobody reported.",
    "seriousness": "Seriousness is not severity. Check each criterion against the facts: a severe headache may be non-serious, a moderate event with hospital admission is serious.",
    "causality": "Answer each Naranjo question from the facts in the case. If the case does not say, choose Don't know.",
    "expectedness": "Compare the reaction with the product information, including its nature, severity and outcome. A fatal outcome is unexpected unless the label describes it.",
    "timeline": "Day Zero is when the minimum criteria were met, or when new information changed the case. Then apply the pathway that fits the product, seriousness and region.",
    "narrative": "Tell the case as a standalone story in time order, with no unsupported inference.",
}

CASES = [
    {
        "id": "PV-001", "title": "Incomplete telephone report from a pharmacist", "level": "Beginner",
        "source": "Telephone report (pharmacist)", "country": "Bulgaria", "received": "2026-11-02",
        "product": "Cardiolux 10 mg", "status": "Marketed", "report_type": "Initial",
        "report": (
            "Call log, 02 Nov 2026, 10:40. The caller identifies herself as Maria Petrova, pharmacist at a "
            "community pharmacy in Plovdiv (phone number recorded). A female customer, about 60 years old, "
            "collected Cardiolux 10 mg tablets last week. She telephoned the pharmacy yesterday saying she had "
            "been 'feeling very unwell since taking the tablets'. The pharmacist has no further details and the "
            "customer left no name."
        ),
        "elements": {
            "patient": (True, "A woman of about 60 identifies a specific patient."),
            "reporter": (True, "A named pharmacist with contact details."),
            "product": (True, "Cardiolux 10 mg is named."),
            "event": (False, "'Feeling unwell' is not a specific adverse event."),
        },
        "followups": [
            {"q": "What exactly did the patient experience, when did it start and how serious was it?", "useful": True, "needed": True,
             "a": "The patient started Cardiolux 10 mg once daily on 30 Oct 2026. On the evening of 1 Nov, about three hours after her third tablet, her lips and tongue swelled. She went to the emergency department and was admitted for observation and IV treatment from 1 to 3 Nov. The doctor documented visible swelling of the lips and tongue."},
            {"q": "Was Cardiolux stopped, and what was the outcome?", "useful": True, "needed": True,
             "a": "Cardiolux was stopped on admission. The swelling resolved within 24 hours and she was discharged on 3 Nov, fully recovered."},
            {"q": "Does the patient take other medicines, or have allergies or earlier episodes of swelling?", "useful": True, "needed": True,
             "a": "She takes no other medicines, has no known allergies and no earlier episodes of swelling. Her only medical history is mild hypertension, the reason for Cardiolux."},
            {"q": "Can you give us the patient's full name and home address?", "useful": False,
             "a": "The pharmacist declines. Personal data should be limited to what is necessary, and the patient is already identifiable by age and sex."},
            {"q": "Please advise the patient to take Cardiolux again to see whether the swelling returns.", "useful": False,
             "a": "Not acceptable. Safety teams do not give medical advice or ask patients to rechallenge. Refer her to the treating doctor."},
        ],
        "reply_date": "04 Nov 2026",
        "code": {"verbatim": "lips and tongue swelled",
                 "options": ["Angioedema", "Swollen lips and swollen tongue", "Anaphylactic shock", "Feeling unwell"],
                 "pt": "Swollen lips and swollen tongue",
                 "why": "No diagnosis was reported, so code the reported signs and do not invent angioedema or anaphylaxis."},
        "ser": {"hosp"}, "flex": {"mie"},
        "ser_note": "Hospital admission makes it serious. Tongue and lip swelling may also be a medically important event, so either choice for that criterion is acceptable.",
        "nj": "nyydndddny", "who": {"Probable/Likely"},
        "nj_note": "Timing fits, the reaction improved after stopping, no other cause was found and a doctor documented the swelling. Rechallenge was not done.",
        "exp_event": "Swelling of the lips and tongue requiring hospital treatment", "exp": "Unexpected",
        "exp_opts": [
            "Skin rash is listed, so any skin or swelling reaction is expected.",
            "Angioedema-type swelling is not listed in section 4.8 and differs in nature from the listed reactions, so it is unexpected.",
            "Expectedness cannot be assessed without the patient's name.",
        ],
        "exp_ok": 1,
        "rule": "EU-PM-SER", "dz": "2026-11-04",
        "dz_note": "The 2 Nov call had a patient, reporter and product but no specific event. The minimum criteria were met only when the follow-up reply arrived on 4 Nov. The case is serious (hospitalisation), so the EU 15-day pathway applies.",
        "facts": [
            ("Patient: woman of about 60", ["60", "woman", "female"]),
            ("Product: Cardiolux 10 mg daily", ["cardiolux"]),
            ("Start date 30 Oct", ["30 oct", "30/10", "october 30", "2026-10-30"]),
            ("Onset on 1 Nov after the third tablet", ["1 nov", "01/11", "november 1", "2026-11-01"]),
            ("Swelling of lips and tongue", ["swell", "oedema", "edema", "angioedema"]),
            ("Hospital admission 1 to 3 Nov", ["hospital", "admitted", "admission", "emergency"]),
            ("Drug stopped", ["stopped", "discontinu", "withdr"]),
            ("Outcome: resolved", ["resolv", "recover"]),
            ("No other medicines; history of hypertension", ["no other", "hypertension", "no concomitant"]),
        ],
    },
    {
        "id": "PV-002", "title": "Consumer reports a severe headache", "level": "Beginner",
        "source": "Online patient report form", "country": "Bulgaria", "received": "2026-11-05",
        "product": "Cardiolux 10 mg", "status": "Marketed", "report_type": "Initial",
        "report": (
            "Web form submitted 05 Nov 2026, 15:12. Reporter: the patient himself (name and email given, consent to "
            "be contacted ticked). Patient: male, 45 years. Product: Cardiolux 10 mg once daily for high blood "
            "pressure, started 3 Nov 2026. Description: 'The next morning I had a terrible pounding headache, the "
            "worst in years. It lasted most of the day. I kept taking the tablets and it is almost gone now. I have "
            "slept badly for weeks because of a new job. I did not go to hospital, I just rested.' Other medicines: "
            "none. Medical history: high blood pressure."
        ),
        "elements": {
            "patient": (True, "Male, 45 years."), "reporter": (True, "The patient, with contact details."),
            "product": (True, "Cardiolux 10 mg."), "event": (True, "A pounding headache starting 4 Nov."),
        },
        "followups": [
            {"q": "Has the headache fully resolved, and is the patient still taking Cardiolux?", "useful": True,
             "a": "The headache was completely gone by the evening of 5 Nov. He is still taking Cardiolux."},
            {"q": "Did the patient seek medical care, or was there any hospital stay?", "useful": True,
             "a": "No medical care was sought and there was no hospital stay."},
            {"q": "Does he take other medicines, and how much coffee or alcohol does he have?", "useful": True,
             "a": "No other medicines. He drinks about four coffees a day."},
            {"q": "Please send a copy of his national ID to verify his identity.", "useful": False,
             "a": "Not needed. The report is already identifiable, and collecting ID documents is excessive."},
            {"q": "Tell the patient to stop taking Cardiolux immediately.", "useful": False,
             "a": "Safety staff do not give medical advice. The patient should speak to his doctor or pharmacist."},
        ],
        "reply_date": "05 Nov 2026",
        "code": {"verbatim": "terrible pounding headache",
                 "options": ["Migraine", "Hypertensive crisis", "Headache", "Insomnia"], "pt": "Headache",
                 "why": "The reporter described a headache. Migraine or hypertensive crisis would be unsupported diagnoses."},
        "ser": set(), "flex": set(),
        "ser_note": "No seriousness criterion applies: no admission, no life threat, no disability. Severe is not the same as serious.",
        "nj": "yyddyddddn", "who": {"Possible"},
        "nj_note": "Headache is a known reaction and the timing fits, but poor sleep and heavy coffee intake are alternative causes, and nothing is objectively confirmed.",
        "exp_event": "Severe headache, resolved while continuing treatment", "exp": "Expected",
        "exp_opts": [
            "Severe headache is unexpected because the label does not mention severity.",
            "It is unexpected because the patient also slept badly.",
            "Headache is listed as common and the description is consistent with the listing, so it is expected.",
        ],
        "exp_ok": 2,
        "rule": "EU-PM-NONSER", "dz": "2026-11-05",
        "dz_note": "A valid consumer report arrived on 5 Nov. The case is non-serious, so the 90 calendar day pathway for non-serious ICSRs from the EEA applies.",
        "facts": [
            ("Patient: man, 45 years", ["45"]), ("Product: Cardiolux 10 mg", ["cardiolux"]),
            ("Start date 3 Nov", ["3 nov", "03/11", "november 3", "2026-11-03"]),
            ("Headache starting the next day (4 Nov)", ["4 nov", "04/11", "next day", "next morning", "2026-11-04"]),
            ("Not hospitalised (non-serious)", ["no hospital", "not hospital", "non-serious", "not serious", "without hospital"]),
            ("Resolved while treatment continued", ["resolv", "recover", "continu", "still taking"]),
            ("No other medicines; hypertension", ["no other", "hypertension", "no concomitant"]),
            ("Possible other factors (poor sleep, coffee)", ["sleep", "coffee", "caffeine"]),
        ],
    },
    {
        "id": "PV-003", "title": "Fatal liver failure reported by a hospital", "level": "Intermediate",
        "source": "Hospital physician email", "country": "Bulgaria", "received": "2026-11-03",
        "product": "Fluvanta 200 mg", "status": "Marketed", "report_type": "Initial",
        "report": (
            "From: Dr N. Georgiev, Department of Gastroenterology, regional hospital (hospital signature and phone "
            "included). Date: 03 Nov 2026. 'I report the death of a 68-year-old woman. She took Fluvanta 200 mg daily "
            "for a fungal nail infection from 6 Oct 2026. She presented on 27 Oct with jaundice, dark urine and "
            "confusion. ALT was 25 times the upper limit of normal and INR 3.1. Diagnosis: acute liver failure. "
            "Fluvanta was stopped on 27 Oct. Despite intensive care she died on 1 Nov 2026. History: type 2 diabetes. "
            "Other medicines: metformin, and paracetamol up to 3 g daily for back pain for several weeks. No alcohol "
            "use reported. Viral hepatitis serology negative.'"
        ),
        "elements": {
            "patient": (True, "Woman, 68 years."), "reporter": (True, "A named physician with hospital contact details."),
            "product": (True, "Fluvanta 200 mg."), "event": (True, "Acute liver failure with death."),
        },
        "followups": [
            {"q": "Please send the available laboratory values and imaging results.", "useful": True,
             "a": "ALT 1,050 U/L (upper limit 40), bilirubin 210 micromol/L, INR 3.1. Ultrasound: normal liver size, no biliary obstruction."},
            {"q": "What were the dose and duration of paracetamol, and was a paracetamol level measured?", "useful": True,
             "a": "Paracetamol up to 3 g daily for about six weeks. No paracetamol level was measured."},
            {"q": "Was an autopsy or a liver biopsy performed?", "useful": True,
             "a": "No autopsy and no biopsy were performed."},
            {"q": "Please confirm that Fluvanta caused the death before we register the case.", "useful": False,
             "a": "Not needed. A suspected relationship is enough for reporting, and causality is assessed by the safety team."},
            {"q": "Send the doctor our promotional brochure for Fluvanta.", "useful": False,
             "a": "Irrelevant to case processing and inappropriate in a safety report."},
        ],
        "reply_date": "03 Nov 2026",
        "code": {"verbatim": "acute liver failure",
                 "options": ["Acute hepatic failure", "Viral hepatitis", "Jaundice", "Drug-induced liver injury, confirmed"],
                 "pt": "Acute hepatic failure",
                 "why": "The physician reported acute liver failure. 'Confirmed drug-induced liver injury' is a causal conclusion, not the reported event."},
        "ser": {"death", "hosp"}, "flex": {"life", "mie"},
        "ser_note": "Death and hospitalisation apply. Life-threatening and medically important event are reasonable to select as well, so either choice is accepted.",
        "nj": "yyndyddddy", "who": {"Possible"},
        "nj_note": "Hepatic reactions are known and the timing fits, with objective laboratory evidence. Paracetamol is a plausible alternative cause, and there was no improvement after stopping.",
        "exp_event": "Acute liver failure with fatal outcome", "exp": "Unexpected",
        "exp_opts": [
            "Elevated liver enzymes are listed, so liver failure is expected.",
            "Fatal cases are always expected.",
            "Only elevated liver enzymes and rare hepatitis are listed. Acute liver failure with a fatal outcome differs in severity, so it is unexpected.",
        ],
        "exp_ok": 2,
        "rule": "EU-PM-SER", "dz": "2026-11-03",
        "dz_note": "All four minimum elements were in the physician's email received on 3 Nov. The case is serious, so in the EU the 15-day pathway applies whether the reaction is expected or not. Expectedness is what separates the US 15-day alert rule.",
        "facts": [
            ("Patient: woman, 68 years", ["68"]), ("Product: Fluvanta 200 mg daily", ["fluvanta"]),
            ("Start date 6 Oct", ["6 oct", "06/10", "october 6", "2026-10-06"]),
            ("Presentation 27 Oct with jaundice and confusion", ["27 oct", "27/10", "jaundice", "2026-10-27"]),
            ("ALT and INR findings", ["alt", "inr"]),
            ("Drug stopped 27 Oct", ["stopped", "discontinu", "withdr"]),
            ("Death on 1 Nov", ["died", "death", "fatal", "1 nov", "2026-11-01"]),
            ("Concomitant paracetamol", ["paracetamol"]),
            ("History: type 2 diabetes", ["diabetes"]),
            ("Missing information (autopsy, paracetamol level)", ["autopsy", "paracetamol level", "not measured", "unknown"]),
        ],
    },
    {
        "id": "PV-004", "title": "A non-serious case becomes serious after follow-up", "level": "Advanced",
        "source": "Patient telephone report, then GP follow-up", "country": "Bulgaria", "received": "2026-10-20",
        "product": "Cardiolux 10 mg", "status": "Marketed", "report_type": "Initial and follow-up",
        "report": (
            "INITIAL REPORT, received 20 Oct 2026 (patient telephone call). A 55-year-old man (name given, contact "
            "recorded) reports a mild itchy red rash on his arms that began on 18 Oct, three days after he started "
            "Cardiolux 10 mg on 15 Oct. He is still taking it. No other symptoms. He takes ibuprofen occasionally for "
            "knee pain. Medical history: hypertension."
        ),
        "docs": [(
            "FOLLOW-UP from the patient's general practitioner, received 04 Nov 2026",
            "Dr Dimitrov (GP, contact on file): 'On 2 Nov the rash spread over his trunk, his face and lips swelled and "
            "he had difficulty breathing. He was admitted to hospital the same day, treated with IV antihistamine and "
            "corticosteroid, and Cardiolux was stopped. The swelling and breathing difficulty resolved by 4 Nov and the "
            "rash is fading. He used ibuprofen 400 mg for his knee on the evening of 1 Nov. He remains in hospital for "
            "observation.'",
        )],
        "elements": {
            "patient": (True, "Male, 55 years."), "reporter": (True, "The patient, and later the named GP."),
            "product": (True, "Cardiolux 10 mg."), "event": (True, "Rash, later facial swelling and breathing difficulty."),
        },
        "followups": [
            {"q": "Please send the hospital discharge letter with outcome and final diagnosis when available.", "useful": True,
             "a": "The discharge letter is expected in about one week."},
            {"q": "Please confirm the date and dose of the last ibuprofen use.", "useful": True,
             "a": "Ibuprofen 400 mg once, on the evening of 1 Nov."},
            {"q": "Was Cardiolux stopped, and on what date?", "useful": True,
             "a": "Cardiolux was stopped on 2 Nov, on admission."},
            {"q": "Ask the GP to restart Cardiolux in hospital to test the reaction.", "useful": False,
             "a": "Not acceptable. Safety staff never ask for a rechallenge, and this could be dangerous."},
            {"q": "Cancel the 20 Oct report because the follow-up replaces it.", "useful": False,
             "a": "Wrong. The initial information stays on the case, and the follow-up is added to it."},
        ],
        "reply_date": "04 Nov 2026",
        "code": {"verbatim": "rash spread, face and lips swelled, difficulty breathing",
                 "options": ["Anaphylactic shock", "Rash only", "Rash, face swelling and dyspnoea (separate terms)", "Allergic reaction only"],
                 "pt": "Rash, face swelling and dyspnoea (separate terms)",
                 "why": "Code each reported event. Anaphylactic shock was not reported as a diagnosis, so do not assume it."},
        "ser": {"hosp"}, "flex": {"life", "mie"},
        "ser_note": "The follow-up shows hospital admission, so the case is now serious. Life-threatening and medically important event are arguable, so either choice is accepted.",
        "nj": "yyydydddny", "who": {"Possible", "Probable/Likely"},
        "nj_note": "Rash is a known reaction, timing fits and the reaction improved after stopping. Ibuprofen is an alternative cause, and the case was objectively documented in hospital.",
        "exp_event": "Rash progressing to facial swelling and breathing difficulty requiring hospital admission", "exp": "Unexpected",
        "exp_opts": [
            "Skin rash is listed, so the whole case is expected.",
            "Rash is listed, but facial swelling with breathing difficulty differs in nature and severity from the listed reactions, so the case as now described is unexpected.",
            "The case is expected because the patient first reported only a mild rash.",
        ],
        "exp_ok": 1,
        "rule": "EU-PM-SER", "dz": "2026-11-04",
        "dz_note": "The 20 Oct report was valid and non-serious (a 90-day case). The follow-up received on 4 Nov contained new medically relevant information that made the case serious, so a new 15-day clock starts on 4 Nov. A simple correction without new information would not restart the clock.",
        "facts": [
            ("Patient: man, 55 years", ["55"]), ("Product: Cardiolux 10 mg", ["cardiolux"]),
            ("Start date 15 Oct", ["15 oct", "15/10", "october 15", "2026-10-15"]),
            ("Rash from 18 Oct", ["18 oct", "18/10", "rash", "2026-10-18"]),
            ("Facial swelling and breathing difficulty on 2 Nov", ["swell", "breath", "dyspn"]),
            ("Hospital admission on 2 Nov", ["hospital", "admitted", "admission"]),
            ("Treatment with antihistamine and corticosteroid", ["antihistamine", "corticosteroid", "steroid"]),
            ("Cardiolux stopped", ["stopped", "discontinu", "withdr"]),
            ("Concomitant ibuprofen", ["ibuprofen"]),
            ("Outcome: improving or resolved", ["resolv", "recover", "improv", "fading"]),
        ],
    },
    {
        "id": "PV-005", "title": "Forum post with a username only", "level": "Beginner",
        "source": "Social media or forum monitoring", "country": "Unknown", "received": "2026-11-06",
        "product": "Cardiolux 10 mg", "status": "Marketed", "report_type": "Initial",
        "report": (
            "Monitoring log, 06 Nov 2026. Public health forum post by the user name 'blue_kite_77' (no real name, no "
            "contact method, private messages disabled): 'Does anyone else get terrible swelling from Cardiolux? Took "
            "it last week and it was awful. Never again.'"
        ),
        "stages": ["validity"],
        "elements": {
            "patient": (False, "No age, sex or other characteristic. A username alone does not prove a real, identifiable patient."),
            "reporter": (False, "No identifiable person and no way to contact them."),
            "product": (True, "Cardiolux is named."),
            "event": (True, "Swelling is mentioned, although it is vague."),
        },
        "followups": [],
        "actions": [
            "Process it as a valid ICSR and report it within 15 days",
            "Document it as not valid because the patient and reporter are not identifiable, and keep it on file in case contact becomes possible",
            "Delete the post from the safety database without any record",
        ],
        "action": "Document it as not valid because the patient and reporter are not identifiable, and keep it on file in case contact becomes possible",
        "action_note": "Record the screening result. Do not report it as a valid case, and do not delete it, because the company may later receive the missing information.",
        "facts": [],
    },
]

REFERENCES = [
    ("ICH E2D(R1)", "Post-approval safety data: definitions, ICSR validity, Day Zero, narratives", "ich.org"),
    ("ICH E2A", "Definition of a serious adverse event", "ich.org"),
    ("EMA Good Pharmacovigilance Practices (GVP), Module VI", "Collection, management and submission of ICSRs in the EU", "ema.europa.eu"),
    ("Regulation (EU) No 536/2014", "Clinical trials and SUSAR reporting", "ema.europa.eu"),
    ("WHO-UMC causality assessment", "Causality categories", "who-umc.org"),
    ("Naranjo et al., 1981", "Adverse drug reaction probability scale", "Clinical Pharmacology and Therapeutics"),
    ("21 CFR 314.80", "US post-marketing reporting of adverse drug experiences", "ecfr.gov"),
]
