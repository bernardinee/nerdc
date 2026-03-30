"""
NERDC Incident Seed Script
==========================
Seeds 32 incidents — 2 per each of Ghana's 16 regions — cycling through
all 8 incident types with full field coverage:
  citizen_name, citizen_phone, incident_type, severity,
  latitude, longitude, address, region, notes

Because the backend silently drops address/region/severity/phone, the script
also prints a JavaScript snippet at the end. Paste it once in your browser
console (DevTools → Console) to inject those extras into localStorage so the
dispatch queue shows full location and severity info.

Run:
    python seed_incidents.py

Requires:  pip install requests
"""

import json
import requests
import sys
import time

# -- Service URLs (Railway, direct — no CORS from Python) ----------------------

AUTH_URL     = "https://auth-service-production-622a.up.railway.app"
INCIDENT_URL = "https://incident-service-production-9dd1.up.railway.app"

# -- System admin credentials --------------------------------------------------

ADMIN_EMAIL    = "admin@nerdc.gov.gh"
ADMIN_PASSWORD = "Admin@1234"

# -- Incident type → backend enum ----------------------------------------------
# Backend only accepts: MEDICAL, FIRE, CRIME, ACCIDENT, OTHER

TYPE_MAP = {
    "fire":           "FIRE",
    "medical":        "MEDICAL",
    "accident":       "ACCIDENT",
    "crime":          "CRIME",
    "flood":          "OTHER",
    "explosion":      "FIRE",
    "missing_person": "OTHER",
    "other":          "OTHER",
}

# -- 32 incidents: 2 per region, all 8 types covered --------------------------
#
# Tuple: (citizen_name, citizen_phone, type, severity, lat, lng, address, region, notes)

INCIDENTS = [
    # ── Greater Accra ─────────────────────────────────────────────────────────
    (
        "Kofi Mensah", "+233244123456",
        "fire", "CRITICAL",
        5.5620, -0.2050,
        "Ring Road Central, near Danquah Circle, Accra",
        "Greater Accra",
        "Structure fire escalating — smoke and heat levels rising. Multiple floors affected. Occupants may still be inside.",
    ),
    (
        "Abena Owusu", "+233200987654",
        "medical", "CRITICAL",
        5.5490, -0.2200,
        "Okaishie Market, Accra Central, Accra",
        "Greater Accra",
        "Individual in critical condition — collapsed at market stall. Unresponsive and struggling to breathe. Immediate care required.",
    ),

    # ── Ashanti ───────────────────────────────────────────────────────────────
    (
        "Yaw Boateng", "+233557891234",
        "accident", "HIGH",
        6.6950, -1.6180,
        "Suame Roundabout, Kumasi",
        "Ashanti",
        "Collision detected at busy roundabout — two vehicles involved, potential injuries and significant vehicle damage. Traffic backing up.",
    ),
    (
        "Ama Frimpong", "+233277654321",
        "crime", "HIGH",
        6.6820, -1.6310,
        "Kejetia Market, Kumasi",
        "Ashanti",
        "Suspicious activity detected — armed individuals reported near market entrance. Possible threat to traders and shoppers.",
    ),

    # ── Western ───────────────────────────────────────────────────────────────
    (
        "Kwame Sarfo", "+233244567890",
        "flood", "HIGH",
        4.9310, -1.7180,
        "Market Circle, Sekondi-Takoradi",
        "Western",
        "Water levels rising rapidly near low-lying market area. Area at risk of submersion — vendors and residents need immediate evacuation.",
    ),
    (
        "Efua Aidoo", "+233209876543",
        "medical", "HIGH",
        4.9380, -1.7080,
        "Takoradi Harbour Road, Sekondi-Takoradi",
        "Western",
        "Individual in critical condition — road traffic victim with head injury. Breathing laboured. Bystanders providing first aid.",
    ),

    # ── Eastern ───────────────────────────────────────────────────────────────
    (
        "Nana Asante", "+233557123456",
        "explosion", "CRITICAL",
        6.0960, -0.2570,
        "Koforidua Industrial Area, Koforidua",
        "Eastern",
        "Blast detected at industrial facility — debris and shockwave impact reported. Several workers unaccounted for. Fire risk high.",
    ),
    (
        "Adjoa Larbi", "+233244890123",
        "missing_person", "MEDIUM",
        6.0910, -0.2610,
        "Koforidua Secondary Technical School, Koforidua",
        "Eastern",
        "Individual unaccounted for — 14-year-old student missing after school hours. Last known location logged near the school gate.",
    ),

    # ── Central ───────────────────────────────────────────────────────────────
    (
        "Kwesi Amponsah", "+233200345678",
        "fire", "HIGH",
        5.1070, -1.2440,
        "Cape Coast Castle Road, Cape Coast",
        "Central",
        "Structure fire escalating — wooden residential building ablaze near the castle road. Smoke visible from a distance. Residents evacuating.",
    ),
    (
        "Akosua Tetteh", "+233277234567",
        "accident", "MEDIUM",
        5.1030, -1.2490,
        "Pedu Junction, Cape Coast",
        "Central",
        "Collision detected — trotro and motorcycle involved at junction. Rider appears injured. Vehicle damage reported. Road partially blocked.",
    ),

    # ── Volta ─────────────────────────────────────────────────────────────────
    (
        "Fiifi Quaye", "+233244678901",
        "crime", "MEDIUM",
        6.6030, 0.4730,
        "Ho Central Market, Ho",
        "Volta",
        "Suspicious activity detected — reports of pickpocketing gang operating in the market. Possible threat to traders and shoppers.",
    ),
    (
        "Akua Danso", "+233557456789",
        "flood", "CRITICAL",
        6.5990, 0.4680,
        "Bankoe Lowlands, Ho",
        "Volta",
        "Water levels rising rapidly — River Volta tributary overflowing into residential area. Families stranded. Area at risk of submersion.",
    ),

    # ── Northern ──────────────────────────────────────────────────────────────
    (
        "Nana Ofori", "+233200123789",
        "medical", "CRITICAL",
        9.4050, -0.8560,
        "Tamale Central Mosque Area, Tamale",
        "Northern",
        "Individual in critical condition — elderly man collapsed during prayers. No pulse detected. CPR being administered by bystander.",
    ),
    (
        "Esi Mensah", "+233244789012",
        "explosion", "HIGH",
        9.4100, -0.8490,
        "Tamale Market, Tamale",
        "Northern",
        "Blast detected — gas cylinder explosion at food vendor stall. Debris and shockwave impact reported. Multiple people near scene.",
    ),

    # ── Upper East ────────────────────────────────────────────────────────────
    (
        "Kojo Frimpong", "+233557890123",
        "accident", "HIGH",
        10.7860, -0.8500,
        "Bolgatanga Main Road, Bolgatanga",
        "Upper East",
        "Collision detected — heavy goods vehicle and passenger bus involved on main road. Multiple potential injuries and significant vehicle damage.",
    ),
    (
        "Adwoa Gyimah", "+233200456789",
        "missing_person", "HIGH",
        10.7830, -0.8530,
        "Bolgatanga Market, Bolgatanga",
        "Upper East",
        "Individual unaccounted for — woman separated from family at market. Last known location logged near the fabric section. Search underway.",
    ),

    # ── Upper West ────────────────────────────────────────────────────────────
    (
        "Yaw Antwi", "+233244901234",
        "fire", "HIGH",
        10.0620, -2.5080,
        "Wa Central, near Regional Hospital, Wa",
        "Upper West",
        "Structure fire escalating — thatched compound house on fire. Smoke and heat levels rising. Families evacuating. Water source scarce.",
    ),
    (
        "Akua Bonsu", "+233277567890",
        "crime", "HIGH",
        10.0580, -2.5120,
        "Wa Market Road, Wa",
        "Upper West",
        "Suspicious activity detected — armed robbery reported at mobile money outlet. Suspect fled on motorbike. Victim injured.",
    ),

    # ── Bono ──────────────────────────────────────────────────────────────────
    (
        "Kwame Osei", "+233557234567",
        "medical", "HIGH",
        7.3360, -2.3260,
        "Sunyani Teaching Hospital Road, Sunyani",
        "Bono",
        "Individual in critical condition — motorcycle accident victim with suspected spinal injury. Not moving. Immediate care required.",
    ),
    (
        "Abena Gyasi", "+233200678901",
        "flood", "MEDIUM",
        7.3320, -2.3310,
        "Sunyani New Site Residential Area, Sunyani",
        "Bono",
        "Water levels rising rapidly — drainage overflow flooding residential neighbourhood. Area at risk of submersion.",
    ),

    # ── Oti ───────────────────────────────────────────────────────────────────
    (
        "Kojo Asante", "+233244012345",
        "accident", "CRITICAL",
        8.0790, 0.1760,
        "Dambai Ferry Landing Approach Road, Dambai",
        "Oti",
        "Collision detected — vehicle drove off ferry approach ramp. Occupants submerged. Potential injuries and drowning risk.",
    ),
    (
        "Adwoa Mensah", "+233557345678",
        "other", "MEDIUM",
        8.0750, 0.1810,
        "Dambai Town Centre, Dambai",
        "Oti",
        "Unknown incident detected — large gathering with reports of altercation. Awaiting classification. Police presence requested.",
    ),

    # ── Savannah ──────────────────────────────────────────────────────────────
    (
        "Kofi Amoah", "+233200789012",
        "fire", "CRITICAL",
        9.0860, -1.8210,
        "Damongo Market Street, Damongo",
        "Savannah",
        "Structure fire escalating — market stalls engulfed in flames. Smoke and heat levels rising. Spread to adjacent structures imminent.",
    ),
    (
        "Akua Larbi", "+233277890123",
        "missing_person", "MEDIUM",
        9.0810, -1.8260,
        "Damongo Junction, Damongo",
        "Savannah",
        "Individual unaccounted for — herdsman missing since morning with livestock. Last known location logged near the town junction.",
    ),

    # ── Bono East ─────────────────────────────────────────────────────────────
    (
        "Yaw Antwi", "+233244123789",
        "explosion", "CRITICAL",
        7.5940, -1.9370,
        "Techiman Fuel Station, Nkrankrom Road, Techiman",
        "Bono East",
        "Blast detected at fuel station — explosion during refuelling. Debris and shockwave impact reported. Fire risk extremely high.",
    ),
    (
        "Esi Boateng", "+233557456012",
        "medical", "MEDIUM",
        7.5900, -1.9410,
        "Holy Family Hospital Road, Techiman",
        "Bono East",
        "Individual in critical condition — pregnant woman in distress with complications. Immediate care required. Family present on scene.",
    ),

    # ── North East ────────────────────────────────────────────────────────────
    (
        "Kwame Sarfo", "+233200901234",
        "crime", "CRITICAL",
        10.5220, -0.3580,
        "Nalerigu Palace Area, Nalerigu",
        "North East",
        "Suspicious activity detected — armed individuals reported near the palace area. Gunshots heard. Possible threat to community.",
    ),
    (
        "Efua Asante", "+233244234567",
        "flood", "HIGH",
        10.5180, -0.3630,
        "Nalerigu-Gambaga Road, Nalerigu",
        "North East",
        "Water levels rising rapidly — road flooded after heavy rains. Vehicles stranded. Area at risk of submersion. Residents need assistance.",
    ),

    # ── Ahafo ─────────────────────────────────────────────────────────────────
    (
        "Nana Amponsah", "+233557678901",
        "accident", "HIGH",
        6.8050, -2.5200,
        "Goaso Town Main Road, Goaso",
        "Ahafo",
        "Collision detected — logging truck overturned on main road. Potential injuries to driver and passersby. Road fully blocked.",
    ),
    (
        "Efua Quaye", "+233277012345",
        "other", "LOW",
        6.8010, -2.5240,
        "Goaso Market Square, Goaso",
        "Ahafo",
        "Unknown incident detected — suspicious package left unattended at market square. Awaiting classification and EOD assessment.",
    ),

    # ── Western North ─────────────────────────────────────────────────────────
    (
        "Kwame Darko", "+233244567123",
        "medical", "HIGH",
        6.2120, -2.4840,
        "Sefwi Wiawso Government Hospital Road, Sefwi Wiawso",
        "Western North",
        "Individual in critical condition — cocoa farm worker bitten by snake. Severe swelling and disorientation. Anti-venom needed urgently.",
    ),
    (
        "Ama Frimpong", "+233557890456",
        "missing_person", "HIGH",
        6.2070, -2.4890,
        "Sefwi Wiawso Forest Edge, Sefwi Wiawso",
        "Western North",
        "Individual unaccounted for — child missing near forest edge at dusk. Last known location logged. Search party forming.",
    ),
]

# ------------------------------------------------------------------------------

def login():
    print("Ensuring admin account exists ...")
    reg_res = requests.post(
        f"{AUTH_URL}/auth/register",
        json={
            "name":       "NERDC Admin",
            "email":      ADMIN_EMAIL,
            "password":   ADMIN_PASSWORD,
            "role":       "SYSTEM_ADMIN",
            "station_id": "NERDC HQ",
        },
        timeout=15,
    )
    if reg_res.status_code == 201:
        print("  Admin account created.")
    elif reg_res.status_code in (400, 409, 422):
        print("  Admin account already exists.")
    else:
        print(f"  Register returned {reg_res.status_code}: {reg_res.text[:200]}")

    print(f"Logging in as {ADMIN_EMAIL} ...")
    res = requests.post(
        f"{AUTH_URL}/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=15,
    )
    if res.status_code != 200:
        print(f"  Login failed: {res.status_code} -- {res.text}")
        sys.exit(1)
    token = res.json()["access_token"]
    print("  Logged in.\n")
    return token


def create_incident(token, name, phone, itype, severity, lat, lng, address, region, notes, retries=4):
    payload = {
        "citizen_name":  name,
        "citizen_phone": phone,
        "incident_type": TYPE_MAP[itype],
        "severity":      severity,
        "latitude":      lat,
        "longitude":     lng,
        "address":       address,
        "region":        region,
        "notes":         notes,
    }
    short_desc = f"{itype.upper():14s}  {region}"
    for attempt in range(1, retries + 1):
        try:
            res = requests.post(
                f"{INCIDENT_URL}/incidents",
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
                timeout=30,
            )
            if res.status_code in (200, 201):
                inc_id = res.json().get("id", "")
                print(f"  [OK]   {str(inc_id):36s}  {short_desc}")
                return inc_id
            else:
                print(f"  [FAIL] {short_desc}  HTTP {res.status_code} -- {res.text[:120]}")
                return None
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            if attempt < retries:
                wait = attempt * 5
                print(f"  [RETRY {attempt}/{retries}] {short_desc} — timeout, waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"  [FAIL] {short_desc}  timeout after {retries} attempts")
                return None


def main():
    token = login()

    print(f"-- Seeding {len(INCIDENTS)} incidents (2 per region, all 8 types) --\n")

    created = []   # list of (id, address, region, severity, phone, notes)
    ok = 0
    fail = 0

    for idx, (name, phone, itype, severity, lat, lng, address, region, notes) in enumerate(INCIDENTS, 1):
        print(f"  [{idx:02d}/{len(INCIDENTS)}] ", end="", flush=True)
        inc_id = create_incident(token, name, phone, itype, severity, lat, lng, address, region, notes)
        if inc_id:
            ok += 1
            created.append((str(inc_id), address, region, severity.lower(), phone, notes))
        else:
            fail += 1
        time.sleep(0.4)

    print(f"\n-- Summary --------------------------------------------------")
    print(f"  Created : {ok}/{len(INCIDENTS)}")
    print(f"  Failed  : {fail}")

    if not created:
        print("\nNo incidents created — nothing to inject.")
        return

    # Build the localStorage extras dict the frontend expects
    extras = {}
    for inc_id, address, region, severity, phone, notes in created:
        extras[inc_id] = {
            "severity":     severity,
            "address":      address,
            "region":       region,
            "citizenPhone": phone,
            "notes":        notes,
        }

    js = (
        "// Paste this entire block into your browser DevTools console\n"
        "// (open DevTools > Console tab > paste > press Enter)\n"
        "// Then hard-refresh the page (Ctrl+Shift+R / Cmd+Shift+R)\n\n"
        f"localStorage.setItem('nerdc_incident_extras', JSON.stringify({json.dumps(extras, indent=2)}));\n"
        "console.log('Location extras injected for "
        + str(len(extras))
        + " incidents. Hard-refresh the page now.');\n"
    )

    # Write console script to a file as well (avoids terminal encoding issues)
    with open("inject_extras.js", "w", encoding="utf-8") as f:
        f.write(js)

    print("\n" + "=" * 70)
    print("BROWSER CONSOLE SCRIPT")
    print("=" * 70)
    print(js)
    print("=" * 70)
    print("\nAlso saved to: inject_extras.js")
    print("\nSteps:")
    print("  1. Open your deployed site in the browser")
    print("  2. Open DevTools (F12 or right-click > Inspect)")
    print("  3. Click the Console tab")
    print("  4. Paste the block above (or copy from inject_extras.js) and press Enter")
    print("  5. Hard-refresh (Ctrl+Shift+R)")
    print("  6. Dispatch queue will now show full location + severity for all seeded incidents.")


if __name__ == "__main__":
    main()
