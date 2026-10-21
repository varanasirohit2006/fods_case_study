import {
  KPIs,
  CityMetric,
  WeatherMetric,
  TrafficMetric,
  VehicleMetric,
  FestivalMetric,
  HourlyMetric,
  PartnerAnalysis,
  TopCombinations,
  DecisionItem,
  FilteredDataResponse,
  PredictionRequest,
  PredictionResponse,
} from './types'
import {
  mockKPIs,
  mockCityData,
  mockWeatherData,
  mockTrafficData,
  mockVehicleData,
  mockFestivalData,
  mockHourlyData,
  mockPartnerAnalysis,
  mockTopCombinations,
  mockDecisions,
  mockSampleOrders,
} from './data/mockData'

// Prefer relative '/api' which Vite proxies to 127.0.0.1:5000, fallback to the direct API
const API_BASE = '/api'
const DIRECT_API_BASE = 'http://127.0.0.1:5000/api'

async function fetchWithFallback<T>(endpoint: string, fallback: T, timeoutMs = 2500): Promise<{ data: T; isLive: boolean }> {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs)

  // Try proxied URL first
  try {
    const res = await fetch(`${API_BASE}${endpoint}`, { signal: controller.signal })
    clearTimeout(timeoutId)
    if (res.ok) {
      const data = await res.json()
      return { data, isLive: true }
    }
  } catch {
    // If proxy fails, attempt direct 127.0.0.1:5000
    try {
      const directController = new AbortController()
      const dTimeout = setTimeout(() => directController.abort(), timeoutMs)
      const directRes = await fetch(`${DIRECT_API_BASE}${endpoint}`, { signal: directController.signal })
      clearTimeout(dTimeout)
      if (directRes.ok) {
        const data = await directRes.json()
        return { data, isLive: true }
      }
    } catch {
      // Backend not running, use verified fallback
    }
  }

  return { data: fallback, isLive: false }
}

export async function fetchKPIs(): Promise<{ data: KPIs; isLive: boolean }> {
  return fetchWithFallback<KPIs>('/kpis', mockKPIs)
}

export async function fetchCityData(): Promise<{ data: CityMetric[]; isLive: boolean }> {
  return fetchWithFallback<CityMetric[]>('/delivery-time/by-city', mockCityData)
}

export async function fetchWeatherData(): Promise<{ data: WeatherMetric[]; isLive: boolean }> {
  return fetchWithFallback<WeatherMetric[]>('/delivery-time/by-weather', mockWeatherData)
}

export async function fetchTrafficData(): Promise<{ data: TrafficMetric[]; isLive: boolean }> {
  return fetchWithFallback<TrafficMetric[]>('/delivery-time/by-traffic', mockTrafficData)
}

export async function fetchVehicleData(): Promise<{ data: VehicleMetric[]; isLive: boolean }> {
  return fetchWithFallback<VehicleMetric[]>('/delivery-time/by-vehicle', mockVehicleData)
}

export async function fetchFestivalData(): Promise<{ data: FestivalMetric[]; isLive: boolean }> {
  return fetchWithFallback<FestivalMetric[]>('/delivery-time/by-festival', mockFestivalData)
}

export async function fetchHourlyData(): Promise<{ data: HourlyMetric[]; isLive: boolean }> {
  return fetchWithFallback<HourlyMetric[]>('/delivery-time/by-hour', mockHourlyData)
}

export async function fetchPartnerAnalysis(): Promise<{ data: PartnerAnalysis; isLive: boolean }> {
  return fetchWithFallback<PartnerAnalysis>('/partner-analysis', mockPartnerAnalysis)
}

export async function fetchTopCombinations(): Promise<{ data: TopCombinations; isLive: boolean }> {
  return fetchWithFallback<TopCombinations>('/top-combinations', mockTopCombinations)
}

export async function fetchDecisions(): Promise<{ data: DecisionItem[]; isLive: boolean }> {
  const result = await fetchWithFallback<{ decisions: DecisionItem[] }>('/decisions', { decisions: mockDecisions })
  const decisions = result.data.decisions || mockDecisions
  // Merge rich images from mock if missing in API response
  const enhanced = decisions.map((d, i) => ({
    ...d,
    image: mockDecisions[i]?.image || d.image,
    tag: mockDecisions[i]?.tag || d.tag,
  }))
  return { data: enhanced, isLive: result.isLive }
}

export async function fetchFilteredOrders(filters: {
  city?: string
  weather?: string
  traffic?: string
  vehicle?: string
  min_time?: number
  max_time?: number
  search?: string
}): Promise<{ data: FilteredDataResponse; isLive: boolean }> {
  const params = new URLSearchParams()
  if (filters.city && filters.city !== 'All') params.append('city', filters.city)
  if (filters.weather && filters.weather !== 'All') params.append('weather', filters.weather)
  if (filters.traffic && filters.traffic !== 'All') params.append('traffic', filters.traffic)
  if (filters.vehicle && filters.vehicle !== 'All') params.append('vehicle', filters.vehicle)
  if (filters.min_time) params.append('min_time', String(filters.min_time))
  if (filters.max_time) params.append('max_time', String(filters.max_time))
  if (filters.search && filters.search.trim()) params.append('search', filters.search.trim())

  const queryString = params.toString() ? `?${params.toString()}` : ''
  const term = (filters.search || '').trim().toLowerCase()
  const filtered = mockSampleOrders.filter(item => {
    if (filters.city && filters.city !== 'All' && item.City.toLowerCase() !== filters.city.toLowerCase()) return false
    if (filters.weather && filters.weather !== 'All' && item.Weather.toLowerCase() !== filters.weather.toLowerCase()) return false
    if (filters.traffic && filters.traffic !== 'All' && item.Traffic.toLowerCase() !== filters.traffic.toLowerCase()) return false
    if (filters.vehicle && filters.vehicle !== 'All' && item.Vehicle_type.toLowerCase() !== filters.vehicle.toLowerCase()) return false
    if (term && !`${item.ID} ${item.Delivery_person_ID} ${item.City} ${item.Weather} ${item.Traffic}`.toLowerCase().includes(term)) return false
    return true
  })
  const fallbackResponse: FilteredDataResponse = {
    total_matching: filtered.length,
    returned: filtered.length,
    data: filtered,
  }

  return fetchWithFallback<FilteredDataResponse>(`/filtered-data${queryString}`, fallbackResponse)
}

export async function predictDeliveryTime(req: PredictionRequest): Promise<{ data: PredictionResponse; isLive: boolean }> {
  const params = new URLSearchParams({
    distance: String(req.distance),
    weather: req.weather,
    traffic: req.traffic,
    city: req.city,
    vehicle: req.vehicle,
    vehicle_condition: String(req.vehicle_condition),
    multiple_deliveries: String(req.multiple_deliveries),
    festival: req.festival,
    age: String(req.age),
    rating: String(req.rating),
    hour: String(req.hour),
  })

  // Offline regression heuristic if backend is offline. Coefficients are
  // anchored to the cleaned dataset's group means (low traffic, sunny, metro).
  let estimate = 17.0 + (req.distance * 1.15)
  if (req.traffic === 'Jam') estimate += 9.7
  else if (req.traffic === 'High') estimate += 5.8
  else if (req.traffic === 'Medium') estimate += 5.2

  if (req.weather === 'Cloudy') estimate += 7.1
  else if (req.weather === 'Fog') estimate += 6.9
  else if (req.weather === 'Windy') estimate += 4.3
  else if (req.weather === 'Sandstorms' || req.weather === 'Stormy') estimate += 4.0

  if (req.festival === 'Yes') estimate += 19.6
  const batchPenalty = [0, 3.8, 17.6, 24.9] // cumulative vs. 0 orders
  estimate += batchPenalty[Math.min(Math.max(req.multiple_deliveries, 0), 3)] || 0
  if (req.vehicle === 'motorcycle') estimate += 3.1
  if (req.city === 'Semi-Urban') estimate += 22.6
  else if (req.city === 'Urban') estimate -= 4.2

  const offlineResponse: PredictionResponse = {
    predicted_delivery_time_min: Math.round(estimate * 10) / 10,
    input_parameters: req,
  }

  // The first live prediction may need to unpickle the model bundle.
  return fetchWithFallback<PredictionResponse>(`/predict?${params.toString()}`, offlineResponse, 12000)
}
