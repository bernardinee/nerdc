import json

created = [
    ("5550c33e-8460-4dca-9570-7c6074a1cb30", "Ring Road Central, near Danquah Circle, Accra", "Greater Accra", "critical", "+233244123456", "Structure fire escalating — smoke and heat levels rising. Multiple floors affected. Occupants may still be inside."),
    ("4b7b6c64-bf69-4d7b-a949-e5f46361801e", "Okaishie Market, Accra Central, Accra", "Greater Accra", "critical", "+233200987654", "Individual in critical condition — collapsed at market stall. Unresponsive and struggling to breathe. Immediate care required."),
    ("d2b60494-64ab-4dfc-96c0-b0525659b6b0", "Suame Roundabout, Kumasi", "Ashanti", "high", "+233557891234", "Collision detected at busy roundabout — two vehicles involved, potential injuries and significant vehicle damage. Traffic backing up."),
    ("528a0139-2bc0-46c3-add2-f2e72ac22c9a", "Kejetia Market, Kumasi", "Ashanti", "high", "+233277654321", "Suspicious activity detected — armed individuals reported near market entrance. Possible threat to traders and shoppers."),
    ("792c0f9a-d993-4849-944a-9e9aa640a8da", "Market Circle, Sekondi-Takoradi", "Western", "high", "+233244567890", "Water levels rising rapidly near low-lying market area. Area at risk of submersion — vendors and residents need immediate evacuation."),
    ("e0380fd2-c605-480f-94cc-81385307e718", "Takoradi Harbour Road, Sekondi-Takoradi", "Western", "high", "+233209876543", "Individual in critical condition — road traffic victim with head injury. Breathing laboured. Bystanders providing first aid."),
    ("ec091100-599b-43de-af10-152e3ccc8e39", "Koforidua Industrial Area, Koforidua", "Eastern", "critical", "+233557123456", "Blast detected at industrial facility — debris and shockwave impact reported. Several workers unaccounted for. Fire risk high."),
    ("f1a26c35-9eaa-4e70-af8b-031e74639dd9", "Koforidua Secondary Technical School, Koforidua", "Eastern", "medium", "+233244890123", "Individual unaccounted for — 14-year-old student missing after school hours. Last known location logged near the school gate."),
    ("65ad15f0-3b66-43d5-b7a8-2f2c85cfc52e", "Cape Coast Castle Road, Cape Coast", "Central", "high", "+233200345678", "Structure fire escalating — wooden residential building ablaze near the castle road. Smoke visible from a distance. Residents evacuating."),
    ("3a3d431e-00a5-435d-9ab7-38f2de8e03c4", "Pedu Junction, Cape Coast", "Central", "medium", "+233277234567", "Collision detected — trotro and motorcycle involved at junction. Rider appears injured. Vehicle damage reported. Road partially blocked."),
    ("8767ea44-da50-4f74-a092-de604556ae6a", "Ho Central Market, Ho", "Volta", "medium", "+233244678901", "Suspicious activity detected — reports of pickpocketing gang operating in the market. Possible threat to traders and shoppers."),
    ("92ca58b6-ae5d-41be-bd9d-297a3898e373", "Bankoe Lowlands, Ho", "Volta", "critical", "+233557456789", "Water levels rising rapidly — River Volta tributary overflowing into residential area. Families stranded. Area at risk of submersion."),
    ("998197d2-952f-4854-8445-c100b3167f02", "Tamale Central Mosque Area, Tamale", "Northern", "critical", "+233200123789", "Individual in critical condition — elderly man collapsed during prayers. No pulse detected. CPR being administered by bystander."),
    ("016a52fd-503e-447c-b939-29bac1e2ed7c", "Tamale Market, Tamale", "Northern", "high", "+233244789012", "Blast detected — gas cylinder explosion at food vendor stall. Debris and shockwave impact reported. Multiple people near scene."),
    ("a441c807-0fe6-42db-966c-916293625ec2", "Bolgatanga Main Road, Bolgatanga", "Upper East", "high", "+233557890123", "Collision detected — heavy goods vehicle and passenger bus involved on main road. Multiple potential injuries and significant vehicle damage."),
    ("6d1828cd-62a2-41ee-adf6-823c7f8ec596", "Bolgatanga Market, Bolgatanga", "Upper East", "high", "+233200456789", "Individual unaccounted for — woman separated from family at market. Last known location logged near the fabric section. Search underway."),
    ("c5e95a2d-d0ad-417f-bfde-72945f2e18d2", "Wa Central, near Regional Hospital, Wa", "Upper West", "high", "+233244901234", "Structure fire escalating — thatched compound house on fire. Smoke and heat levels rising. Families evacuating. Water source scarce."),
    ("d8a0c5dd-8ed7-4565-98be-fb2d801fcd10", "Wa Market Road, Wa", "Upper West", "high", "+233277567890", "Suspicious activity detected — armed robbery reported at mobile money outlet. Suspect fled on motorbike. Victim injured."),
    ("1d6d3f80-2575-44b7-b8ef-c096f373d6b8", "Sunyani Teaching Hospital Road, Sunyani", "Bono", "high", "+233557234567", "Individual in critical condition — motorcycle accident victim with suspected spinal injury. Not moving. Immediate care required."),
    ("1fd8a0de-19fe-4314-bff6-3fd2d217893b", "Sunyani New Site Residential Area, Sunyani", "Bono", "medium", "+233200678901", "Water levels rising rapidly — drainage overflow flooding residential neighbourhood. Area at risk of submersion."),
    ("aa75eb5a-27b0-4728-a78b-bf70203ec23d", "Dambai Ferry Landing Approach Road, Dambai", "Oti", "critical", "+233244012345", "Collision detected — vehicle drove off ferry approach ramp. Occupants submerged. Potential injuries and drowning risk."),
    ("48045aab-293a-47eb-8c2c-69d679187e8a", "Dambai Town Centre, Dambai", "Oti", "medium", "+233557345678", "Unknown incident detected — large gathering with reports of altercation. Awaiting classification. Police presence requested."),
    ("ba0de934-1c6f-4bd9-952f-09208905c676", "Damongo Market Street, Damongo", "Savannah", "critical", "+233200789012", "Structure fire escalating — market stalls engulfed in flames. Smoke and heat levels rising. Spread to adjacent structures imminent."),
    ("562aea62-00e1-4e70-bcbc-0c9cdc89c66a", "Damongo Junction, Damongo", "Savannah", "medium", "+233277890123", "Individual unaccounted for — herdsman missing since morning with livestock. Last known location logged near the town junction."),
    ("8920fbf3-8e96-4356-be31-c546cabf50c0", "Techiman Fuel Station, Nkrankrom Road, Techiman", "Bono East", "critical", "+233244123789", "Blast detected at fuel station — explosion during refuelling. Debris and shockwave impact reported. Fire risk extremely high."),
    ("619a2b23-9c21-4f4f-8fa7-b3ff57a7ed8a", "Holy Family Hospital Road, Techiman", "Bono East", "medium", "+233557456012", "Individual in critical condition — pregnant woman in distress with complications. Immediate care required. Family present on scene."),
    ("d4726370-42fe-47cf-91af-b17e2e2dac47", "Nalerigu Palace Area, Nalerigu", "North East", "critical", "+233200901234", "Suspicious activity detected — armed individuals reported near the palace area. Gunshots heard. Possible threat to community."),
    ("1c4a537a-0752-400f-a780-663688613838", "Nalerigu-Gambaga Road, Nalerigu", "North East", "high", "+233244234567", "Water levels rising rapidly — road flooded after heavy rains. Vehicles stranded. Area at risk of submersion. Residents need assistance."),
    ("8b2d97a8-4540-4ee9-b06e-f413ff5fb435", "Goaso Town Main Road, Goaso", "Ahafo", "high", "+233557678901", "Collision detected — logging truck overturned on main road. Potential injuries to driver and passersby. Road fully blocked."),
    ("3dc84963-82ab-428b-880b-b98a690b89fe", "Goaso Market Square, Goaso", "Ahafo", "low", "+233277012345", "Unknown incident detected — suspicious package left unattended at market square. Awaiting classification and EOD assessment."),
    ("44a0d39b-95ec-48f7-9c35-53d4a5ce86e3", "Sefwi Wiawso Government Hospital Road, Sefwi Wiawso", "Western North", "high", "+233244567123", "Individual in critical condition — cocoa farm worker bitten by snake. Severe swelling and disorientation. Anti-venom needed urgently."),
    ("55678e72-221b-462a-9c93-e2f08b670441", "Sefwi Wiawso Forest Edge, Sefwi Wiawso", "Western North", "high", "+233557890456", "Individual unaccounted for — child missing near forest edge at dusk. Last known location logged. Search party forming."),
]

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
    "// Paste into browser DevTools > Console, then press Enter\n"
    "localStorage.setItem('nerdc_incident_extras', JSON.stringify("
    + json.dumps(extras)
    + "));\nwindow.location.reload();\n"
)

with open("inject_extras.js", "w", encoding="utf-8") as f:
    f.write(js)

print("inject_extras.js generated for", len(extras), "incidents.")
