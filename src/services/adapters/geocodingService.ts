// Uses Nominatim — OpenStreetMap's free reverse geocoding API.
// No API key, no account, no billing required.
// Rate limit: 1 request/second (fine for manual map clicks).
//
// TODO: When backend is ready you can optionally proxy this through your server
// to avoid CORS restrictions in production, or swap for a paid geocoding API.

export interface ReverseGeocodeResult {
  /** Formatted street address (house number + road) */
  address: string
  /** Full display name from Nominatim */
  displayName: string
  /** Ghana region, normalised to match the form's select options */
  region: string
  /** City / town */
  city: string
  /** Country */
  country: string
}

// ─── Instant offline region derivation ───────────────────────────────────────
// Uses approximate bounding boxes for Ghana's 16 regions.
// No network call — returns immediately so the dispatch queue never shows blanks.

interface RegionBounds {
  region: string
  capital: string
  latMin: number; latMax: number
  lngMin: number; lngMax: number
}

const REGION_BOUNDS: RegionBounds[] = [
  // More specific/smaller first to avoid being swallowed by larger neighbours
  { region: 'Greater Accra', capital: 'Accra',        latMin: 5.47,  latMax: 5.95,  lngMin: -0.40, lngMax:  0.20 },
  { region: 'Upper East',    capital: 'Bolgatanga',   latMin: 10.05, latMax: 11.20, lngMin: -1.05, lngMax:  0.60 },
  { region: 'Upper West',    capital: 'Wa',           latMin:  9.50, latMax: 11.10, lngMin: -2.85, lngMax: -1.05 },
  { region: 'North East',    capital: 'Nalerigu',     latMin:  9.85, latMax: 10.90, lngMin: -0.50, lngMax:  0.55 },
  { region: 'Savannah',      capital: 'Damongo',      latMin:  8.45, latMax: 10.50, lngMin: -2.80, lngMax: -0.50 },
  { region: 'Northern',      capital: 'Tamale',       latMin:  8.45, latMax: 10.75, lngMin: -0.50, lngMax:  0.50 },
  { region: 'Oti',           capital: 'Dambai',       latMin:  7.50, latMax:  8.85, lngMin: -0.15, lngMax:  0.75 },
  { region: 'Bono East',     capital: 'Techiman',     latMin:  7.15, latMax:  8.45, lngMin: -1.05, lngMax:  0.05 },
  { region: 'Ahafo',         capital: 'Goaso',        latMin:  6.85, latMax:  7.80, lngMin: -2.55, lngMax: -1.55 },
  { region: 'Brong-Ahafo',   capital: 'Sunyani',      latMin:  7.10, latMax:  8.45, lngMin: -2.80, lngMax: -1.05 },
  { region: 'Volta',         capital: 'Ho',           latMin:  5.75, latMax:  7.50, lngMin: -0.15, lngMax:  0.80 },
  { region: 'Eastern',       capital: 'Koforidua',    latMin:  5.80, latMax:  6.90, lngMin: -0.53, lngMax:  0.20 },
  { region: 'Ashanti',       capital: 'Kumasi',       latMin:  5.75, latMax:  7.60, lngMin: -2.55, lngMax: -0.53 },
  { region: 'Western North', capital: 'Sefwi Wiawso', latMin:  5.55, latMax:  7.35, lngMin: -3.20, lngMax: -2.00 },
  { region: 'Central',       capital: 'Cape Coast',   latMin:  4.93, latMax:  5.97, lngMin: -1.70, lngMax: -0.40 },
  { region: 'Western',       capital: 'Takoradi',     latMin:  4.50, latMax:  6.60, lngMin: -3.24, lngMax: -1.70 },
]

/** Instant, offline fallback — derives region and a rough address from coordinates. */
export function deriveLocationFromCoords(lat: number, lng: number): { address: string; region: string } {
  const match = REGION_BOUNDS.find(
    (b) => lat >= b.latMin && lat <= b.latMax && lng >= b.lngMin && lng <= b.lngMax,
  )
  const region  = match?.region  ?? 'Greater Accra'
  const capital = match?.capital ?? 'Accra'
  return { address: `${capital} area`, region }
}

// Map Nominatim state/region strings → form select values
const REGION_MAP: Record<string, string> = {
  'greater accra':  'Greater Accra',
  'ashanti':        'Ashanti',
  'western':        'Western',
  'eastern':        'Eastern',
  'central':        'Central',
  'volta':          'Volta',
  'northern':       'Northern',
  'upper east':     'Upper East',
  'upper west':     'Upper West',
  'brong-ahafo':    'Brong-Ahafo',
  'bono':           'Brong-Ahafo',   // older Bono region maps here
  'oti':            'Oti',
  'savannah':       'Savannah',
  'bono east':      'Bono East',
  'north east':     'North East',
  'ahafo':          'Ahafo',
  'western north':  'Western North',
}

function normaliseRegion(raw: string | undefined): string {
  if (!raw) return 'Greater Accra'
  // Strip " Region" suffix Nominatim sometimes appends
  const cleaned = raw.replace(/\s*region$/i, '').trim().toLowerCase()
  return REGION_MAP[cleaned] ?? raw.replace(/\s*region$/i, '').trim()
}

interface NominatimAddress {
  house_number?: string
  road?: string
  suburb?: string
  neighbourhood?: string
  village?: string
  town?: string
  city?: string
  county?: string
  state?: string
  country?: string
}

interface NominatimResponse {
  display_name?: string
  address?: NominatimAddress
  error?: string
}

export async function reverseGeocode(lat: number, lng: number): Promise<ReverseGeocodeResult> {
  const url =
    `https://nominatim.openstreetmap.org/reverse` +
    `?format=json&lat=${lat}&lon=${lng}&addressdetails=1&accept-language=en`

  const res = await fetch(url)

  if (!res.ok) throw new Error(`Geocoding failed: ${res.statusText}`)

  const data: NominatimResponse = await res.json()

  if (data.error) throw new Error(data.error)

  const a = data.address ?? {}


  const parts: string[] = []
  if (a.house_number) parts.push(a.house_number)
  if (a.road)         parts.push(a.road)
  else if (a.suburb)  parts.push(a.suburb)
  else if (a.neighbourhood) parts.push(a.neighbourhood)
  else if (a.village) parts.push(a.village)

  const city = a.city ?? a.town ?? a.county ?? ''
  if (city && !parts.includes(city)) parts.push(city)

  const address = parts.join(', ') || data.display_name?.split(',').slice(0, 2).join(',').trim() || `${lat.toFixed(5)}, ${lng.toFixed(5)}`

  return {
    address,
    displayName: data.display_name ?? address,
    region: normaliseRegion(a.state),
    city,
    country: a.country ?? 'Ghana',
  }
}
