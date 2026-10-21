export interface KPIs {
  total_orders: number
  total_delivery_partners: number
  avg_delivery_time: number
  median_delivery_time: number
  avg_rating: number
  total_cities: number
  date_range: string
  avg_distance_km: number
  median_distance_km: number
  p99_distance_km: number
}

export interface CityMetric {
  city: string
  mean_time: number
  median_time: number
  std_time: number
  order_count: number
}

export interface WeatherMetric {
  weather: string
  mean_time: number
  median_time: number
  std_time: number
  order_count: number
}

export interface TrafficMetric {
  traffic: string
  mean_time: number
  median_time: number
  std_time: number
  order_count: number
}

export interface VehicleMetric {
  vehicle_type: string
  mean_time: number
  median_time: number
  std_time: number
  order_count: number
}

export interface FestivalMetric {
  festival: string
  mean_time: number
  median_time: number
  std_time: number
  order_count: number
}

export interface HourlyMetric {
  hour: number
  mean_time: number
  order_count: number
}

export interface PartnerAnalysis {
  avg_age: number
  avg_rating: number
  total_partners: number
  vehicle_distribution: Record<string, number>
  avg_delivery_time_by_age_group?: Record<string, number>
  avg_delivery_time_by_batching?: Record<string, number>
}

export interface CombinationItem {
  city: string
  weather: string
  traffic: string
  mean_time: number
  median_time: number
  order_count: number
}

export interface TopCombinations {
  slowest_10: CombinationItem[]
  fastest_10: CombinationItem[]
}

export interface DecisionItem {
  id: number
  title: string
  evidence: string
  impact: string
  tag?: string
  image?: string
}

export interface FilteredOrder {
  ID: string
  Delivery_person_ID: string
  Age: number
  Rating: number
  Weather: string
  Traffic: string
  Vehicle_condition: number
  Vehicle_type: string
  multiple_deliveries: number
  Festival: string
  City: string
  Time_taken_min: number
  distance_km?: number
  hour?: number
  Order_Date?: string
}

export interface FilteredDataResponse {
  total_matching: number
  returned: number
  data: FilteredOrder[]
}

export interface PredictionRequest {
  distance: number
  weather: string
  traffic: string
  city: string
  vehicle: string
  vehicle_condition: number
  multiple_deliveries: number
  festival: string
  age: number
  rating: number
  hour: number
}

export interface ModelMetrics {
  r2: number
  mae: number
  rmse: number
  n_train: number
  n_test: number
}

export interface PredictionResponse {
  predicted_delivery_time_min: number
  input_parameters: PredictionRequest
  model_metrics?: ModelMetrics
}
