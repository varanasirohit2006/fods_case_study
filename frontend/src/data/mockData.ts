import { KPIs, CityMetric, WeatherMetric, TrafficMetric, VehicleMetric, FestivalMetric, HourlyMetric, PartnerAnalysis, DecisionItem, FilteredOrder, TopCombinations } from '../types'

export const REAL_IMAGES = {
  heroRider: 'https://images.unsplash.com/photo-1617347454431-f49d7ff5c3b1?auto=format&fit=crop&w=1200&q=80',
  deliveryScooter: 'https://images.unsplash.com/photo-1526367790999-0150786686a2?auto=format&fit=crop&w=1000&q=80',
  deliveryBag: 'https://images.unsplash.com/photo-1585515320310-259814833e62?auto=format&fit=crop&w=800&q=80',
  biryani: 'https://images.unsplash.com/photo-1589302168068-964664d93dc0?auto=format&fit=crop&w=800&q=80',
  pizza: 'https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=800&q=80',
  burger: 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=800&q=80',
  rainDelivery: 'https://images.unsplash.com/photo-1534274988757-a28bf1a57c17?auto=format&fit=crop&w=800&q=80',
  heavyTraffic: 'https://images.unsplash.com/photo-1506521781263-d8422e82f27a?auto=format&fit=crop&w=800&q=80',
  nightCity: 'https://images.unsplash.com/photo-1519501025264-65ba15a82390?auto=format&fit=crop&w=800&q=80',
  festival: 'https://images.unsplash.com/photo-1514565131-fce0801e5785?auto=format&fit=crop&w=800&q=80',
  electricScooter: 'https://images.unsplash.com/photo-1558981806-ec527fa84c39?auto=format&fit=crop&w=800&q=80',
  partnerMeeting: 'https://images.unsplash.com/photo-1556740758-90de374c12ad?auto=format&fit=crop&w=800&q=80',
  kitchenPrep: 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=800&q=80',
}

export const mockKPIs: KPIs = {
  total_orders: 45584,
  total_delivery_partners: 1320,
  avg_delivery_time: 26.29,
  median_delivery_time: 26,
  avg_rating: 4.64,
  total_cities: 3,
  date_range: '2022-02-11 to 2022-04-06',
  avg_distance_km: 9.74,
  median_distance_km: 9.22,
  p99_distance_km: 20.56,
}

export const mockCityData: CityMetric[] = [
  { city: 'Semi-Urban', mean_time: 49.73, median_time: 49, std_time: 2.69, order_count: 164 },
  { city: 'Metropolitian', mean_time: 27.14, median_time: 26, std_time: 9.21, order_count: 35287 },
  { city: 'Urban', mean_time: 22.98, median_time: 22, std_time: 8.87, order_count: 10133 },
]

export const mockWeatherData: WeatherMetric[] = [
  { weather: 'Cloudy', mean_time: 28.92, median_time: 28, std_time: 10.09, order_count: 7533 },
  { weather: 'Fog', mean_time: 28.74, median_time: 28, std_time: 10.1, order_count: 8269 },
  { weather: 'Windy', mean_time: 26.12, median_time: 26, std_time: 8.62, order_count: 7422 },
  { weather: 'Sandstorms', mean_time: 25.88, median_time: 26, std_time: 8.62, order_count: 7494 },
  { weather: 'Stormy', mean_time: 25.87, median_time: 26, std_time: 8.47, order_count: 7584 },
  { weather: 'Sunny', mean_time: 21.86, median_time: 20, std_time: 8.33, order_count: 7282 },
]

export const mockTrafficData: TrafficMetric[] = [
  { traffic: 'Jam', mean_time: 31.18, median_time: 31, std_time: 9.94, order_count: 14139 },
  { traffic: 'High', mean_time: 27.24, median_time: 27, std_time: 8.4, order_count: 4423 },
  { traffic: 'Medium', mean_time: 26.7, median_time: 27, std_time: 8.56, order_count: 10945 },
  { traffic: 'Low', mean_time: 21.46, median_time: 21, std_time: 6.99, order_count: 16077 },
]

export const mockVehicleData: VehicleMetric[] = [
  { vehicle_type: 'motorcycle', mean_time: 27.61, median_time: 26, std_time: 9.65, order_count: 26429 },
  { vehicle_type: 'bicycle', mean_time: 26.43, median_time: 26, std_time: 9.26, order_count: 68 },
  { vehicle_type: 'scooter', mean_time: 24.48, median_time: 24, std_time: 8.7, order_count: 15273 },
  { vehicle_type: 'electric_scooter', mean_time: 24.47, median_time: 24, std_time: 8.61, order_count: 3814 },
]

export const mockFestivalData: FestivalMetric[] = [
  { festival: 'Yes', mean_time: 45.52, median_time: 45, std_time: 4, order_count: 896 },
  { festival: 'No', mean_time: 25.91, median_time: 25, std_time: 9.05, order_count: 44688 },
]

export const mockHourlyData: HourlyMetric[] = [
  { hour: 0, mean_time: 22.38, order_count: 489 },
  { hour: 8, mean_time: 19.56, order_count: 1882 },
  { hour: 9, mean_time: 19.49, order_count: 2040 },
  { hour: 10, mean_time: 19.5, order_count: 2065 },
  { hour: 11, mean_time: 26.32, order_count: 2026 },
  { hour: 12, mean_time: 26.96, order_count: 931 },
  { hour: 13, mean_time: 27.67, order_count: 822 },
  { hour: 14, mean_time: 27.58, order_count: 824 },
  { hour: 15, mean_time: 23.23, order_count: 909 },
  { hour: 16, mean_time: 22.96, order_count: 738 },
  { hour: 17, mean_time: 27.41, order_count: 4407 },
  { hour: 18, mean_time: 27.25, order_count: 4661 },
  { hour: 19, mean_time: 30.81, order_count: 4766 },
  { hour: 20, mean_time: 31.2, order_count: 4708 },
  { hour: 21, mean_time: 31.14, order_count: 4865 },
  { hour: 22, mean_time: 23.22, order_count: 4762 },
  { hour: 23, mean_time: 22.44, order_count: 4689 },
]

export const mockPartnerAnalysis: PartnerAnalysis = {
  avg_age: 29.6,
  avg_rating: 4.64,
  total_partners: 1320,
  vehicle_distribution: {
    bicycle: 68,
    electric_scooter: 3814,
    motorcycle: 26429,
    scooter: 15273,
  },
  avg_delivery_time_by_age_group: {
    '15-25': 22.98,
    '26-30': 24.59,
    '31-35': 29.65,
    '36-40': 29.48,
    '41-50': 23.94,
  },
  avg_delivery_time_by_batching: {
    '0': 22.88,
    '1': 26.72,
    '2': 40.45,
    '3': 47.82,
  },
}

export const mockTopCombinations: TopCombinations = {
  slowest_10: [
    { city: 'Semi-Urban', weather: 'Sandstorms', traffic: 'Jam', mean_time: 50.93, median_time: 52, order_count: 15 },
    { city: 'Semi-Urban', weather: 'Windy', traffic: 'Jam', mean_time: 50.71, median_time: 50, order_count: 17 },
    { city: 'Semi-Urban', weather: 'Stormy', traffic: 'Jam', mean_time: 49.76, median_time: 49, order_count: 17 },
    { city: 'Semi-Urban', weather: 'Fog', traffic: 'Jam', mean_time: 49.67, median_time: 49, order_count: 30 },
    { city: 'Semi-Urban', weather: 'Cloudy', traffic: 'Jam', mean_time: 49.53, median_time: 49, order_count: 45 },
    { city: 'Semi-Urban', weather: 'Sunny', traffic: 'Jam', mean_time: 49.45, median_time: 49, order_count: 11 },
    { city: 'Metropolitian', weather: 'Fog', traffic: 'Jam', mean_time: 36.97, median_time: 37, order_count: 2033 },
    { city: 'Metropolitian', weather: 'Cloudy', traffic: 'Jam', mean_time: 36.62, median_time: 37, order_count: 1971 },
    { city: 'Urban', weather: 'Cloudy', traffic: 'Jam', mean_time: 35.39, median_time: 35, order_count: 332 },
    { city: 'Urban', weather: 'Fog', traffic: 'Jam', mean_time: 34.86, median_time: 35, order_count: 368 },
  ],
  fastest_10: [
    { city: 'Urban', weather: 'Sandstorms', traffic: 'Low', mean_time: 18.38, median_time: 18, order_count: 720 },
    { city: 'Urban', weather: 'Sunny', traffic: 'Medium', mean_time: 18.8, median_time: 18, order_count: 484 },
    { city: 'Urban', weather: 'Stormy', traffic: 'Low', mean_time: 18.95, median_time: 19, order_count: 724 },
    { city: 'Urban', weather: 'Windy', traffic: 'Low', mean_time: 19.08, median_time: 19, order_count: 635 },
    { city: 'Urban', weather: 'Sunny', traffic: 'High', mean_time: 19.15, median_time: 17, order_count: 197 },
    { city: 'Urban', weather: 'Sunny', traffic: 'Low', mean_time: 19.19, median_time: 18, order_count: 659 },
    { city: 'Urban', weather: 'Cloudy', traffic: 'Low', mean_time: 19.9, median_time: 18, order_count: 691 },
    { city: 'Urban', weather: 'Fog', traffic: 'Low', mean_time: 20.42, median_time: 19, order_count: 778 },
    { city: 'Urban', weather: 'Sunny', traffic: 'Jam', mean_time: 20.64, median_time: 19, order_count: 588 },
    { city: 'Metropolitian', weather: 'Sunny', traffic: 'Medium', mean_time: 20.72, median_time: 19, order_count: 1300 },
  ],
}

export const mockDecisions: DecisionItem[] = [
  {
    id: 1,
    title: 'Dynamic Traffic & Weather ETA Buffering',
    evidence: 'Jam traffic averages 31.18 min vs 21.46 min in Low traffic (+9.71 min; z = +96.98, p < 1e-15). Cloudy and Fog average 28.92 and 28.74 min vs 21.86 min in Sunny conditions (+7.06 min max).',
    impact: 'Adds +10 min buffers in jams and +7 min in low-visibility weather, reducing SLA breaches without padding every order.',
    tag: 'ETA Policy',
    image: REAL_IMAGES.heavyTraffic,
  },
  {
    id: 2,
    title: 'Fleet Electrification & Scooter Prioritization',
    evidence: 'Scooters average 24.48 min and electric scooters 24.47 min vs 27.61 min for motorcycles (3.13 min faster; permutation p < 0.0002).',
    impact: 'Saves about 3.1 minutes per delivery while cutting fuel emissions on metro routes.',
    tag: 'Fleet Strategy',
    image: REAL_IMAGES.electricScooter,
  },
  {
    id: 3,
    title: 'Holiday & Festival Surge Fleet Deployment (+30%)',
    evidence: 'Festival deliveries average 45.52 min vs 25.91 min on normal days (+19.61 min; z = +139.68, p < 1e-15; 896 vs 44,688 orders).',
    impact: 'Deploys 30% additional fleet and premium surge payouts to protect sub-35 min SLAs during festivals.',
    tag: 'Surge Operations',
    image: REAL_IMAGES.festival,
  },
  {
    id: 4,
    title: 'Vehicle Condition Floor (Condition >= 1)',
    evidence: 'Condition-0 vehicles average 30.07 min vs 24.35 min for condition 1 and 24.45 min for condition 2 (n = 15,005 vs ~15,000 each). Condition 3 is a small non-monotonic group (26.49 min, n = 520).',
    impact: 'Rejects condition-0 vehicles at onboarding, cutting a 5.7 min penalty; flags condition-3 vehicles for inspection.',
    tag: 'Fleet Maintenance',
    image: REAL_IMAGES.deliveryScooter,
  },
  {
    id: 5,
    title: 'Strict Order Batching Caps (Max 2 Orders)',
    evidence: 'Solo = 22.88 min; 1 stacked = 26.72 min; 2 = 40.45 min; 3 = 47.82 min. A second order adds +13.73 min and three orders vs solo +24.94 min (permutation p < 0.0002).',
    impact: 'Caps simultaneous dispatches at two and eliminates 3-order windows that erase per-customer transit gains.',
    tag: 'Dispatch Algorithm',
    image: REAL_IMAGES.deliveryBag,
  },
  {
    id: 6,
    title: 'High-Rated Partner Routing for Premium & Far Deliveries',
    evidence: 'Partners rated 4.5+ average 24.42 min vs 37.37 min for the 2.0-3.0 band (12.95 min faster); the 31-35 age band averages 29.65 min.',
    impact: 'Routes high-value family meals and long-distance orders to the highest-rated partners.',
    tag: 'Rider Allocation',
    image: REAL_IMAGES.heroRider,
  },
  {
    id: 7,
    title: 'Hub Pre-Positioning Ahead of Dinner Peak (7-9 PM)',
    evidence: 'Volume rises from 2,065 orders at 10 AM to 4,865 at 9 PM; the 7-9 PM dinner window averages 31.05 min vs 19.52 min in the 8-10 AM morning window (+11.53 min).',
    impact: 'Pre-positions riders near high-density cloud kitchens by 6:45 PM, cutting pickup latency during the dinner surge.',
    tag: 'Demand Synchrony',
    image: REAL_IMAGES.kitchenPrep,
  },
]

export const mockSampleOrders: FilteredOrder[] = [
  { ID: '0xcdcd', Delivery_person_ID: 'DEHRES17DEL01', Age: 36, Rating: 4.2, Weather: 'Fog', Traffic: 'Jam', Vehicle_condition: 2, Vehicle_type: 'motorcycle', multiple_deliveries: 3, Festival: 'No', City: 'Metropolitian', Time_taken_min: 46, distance_km: 10.28, hour: 21, Order_Date: '2022-02-12' },
  { ID: '0xd987', Delivery_person_ID: 'KOCRES16DEL01', Age: 21, Rating: 4.7, Weather: 'Stormy', Traffic: 'High', Vehicle_condition: 1, Vehicle_type: 'motorcycle', multiple_deliveries: 1, Festival: 'No', City: 'Metropolitian', Time_taken_min: 23, distance_km: 6.24, hour: 14, Order_Date: '2022-02-13' },
  { ID: '0x2784', Delivery_person_ID: 'PUNERES13DEL03', Age: 23, Rating: 4.7, Weather: 'Sandstorms', Traffic: 'Medium', Vehicle_condition: 1, Vehicle_type: 'scooter', multiple_deliveries: 1, Festival: 'No', City: 'Metropolitian', Time_taken_min: 21, distance_km: 13.79, hour: 17, Order_Date: '2022-03-04' },
  { ID: '0xc8b6', Delivery_person_ID: 'LUDHRES15DEL02', Age: 34, Rating: 4.3, Weather: 'Sandstorms', Traffic: 'Low', Vehicle_condition: 0, Vehicle_type: 'motorcycle', multiple_deliveries: 0, Festival: 'No', City: 'Metropolitian', Time_taken_min: 20, distance_km: 2.93, hour: 9, Order_Date: '2022-02-13' },
  { ID: '0xdb64', Delivery_person_ID: 'KNPRES14DEL02', Age: 24, Rating: 4.7, Weather: 'Fog', Traffic: 'Jam', Vehicle_condition: 1, Vehicle_type: 'scooter', multiple_deliveries: 1, Festival: 'No', City: 'Metropolitian', Time_taken_min: 41, distance_km: 19.4, hour: 19, Order_Date: '2022-02-14' },
  { ID: '0x3af3', Delivery_person_ID: 'MUMRES15DEL03', Age: 29, Rating: 4.5, Weather: 'Sandstorms', Traffic: 'Jam', Vehicle_condition: 2, Vehicle_type: 'electric_scooter', multiple_deliveries: 1, Festival: 'No', City: 'Metropolitian', Time_taken_min: 20, distance_km: 13.76, hour: 20, Order_Date: '2022-04-02' },
  { ID: '0x3aab', Delivery_person_ID: 'MYSRES01DEL01', Age: 35, Rating: 4, Weather: 'Windy', Traffic: 'High', Vehicle_condition: 1, Vehicle_type: 'scooter', multiple_deliveries: 1, Festival: 'No', City: 'Metropolitian', Time_taken_min: 33, distance_km: 6.22, hour: 14, Order_Date: '2022-03-01' },
  { ID: '0x5795', Delivery_person_ID: 'RANCHIRES06DEL02', Age: 31, Rating: 4.7, Weather: 'Sandstorms', Traffic: 'Low', Vehicle_condition: 2, Vehicle_type: 'electric_scooter', multiple_deliveries: 0, Festival: 'No', City: 'Metropolitian', Time_taken_min: 26, distance_km: 19.62, hour: 22, Order_Date: '2022-03-10' },
  { ID: '0xa1b2', Delivery_person_ID: 'CHENRES01DEL01', Age: 29, Rating: 4.5, Weather: 'Sunny', Traffic: 'Medium', Vehicle_condition: 2, Vehicle_type: 'electric_scooter', multiple_deliveries: 1, Festival: 'No', City: 'Metropolitian', Time_taken_min: 15, distance_km: 17.08, hour: 18, Order_Date: '2022-03-27' },
  { ID: '0x8bc0', Delivery_person_ID: 'SURRES15DEL03', Age: 35, Rating: 4.3, Weather: 'Cloudy', Traffic: 'Low', Vehicle_condition: 1, Vehicle_type: 'scooter', multiple_deliveries: 0, Festival: 'No', City: 'Metropolitian', Time_taken_min: 38, distance_km: 13.68, hour: 23, Order_Date: '2022-03-12' },
]
