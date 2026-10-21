import React, { useState, useEffect, useCallback } from 'react'
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
} from './types'
import {
  fetchKPIs,
  fetchCityData,
  fetchWeatherData,
  fetchTrafficData,
  fetchVehicleData,
  fetchFestivalData,
  fetchHourlyData,
  fetchPartnerAnalysis,
  fetchTopCombinations,
  fetchDecisions,
} from './api'
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
} from './data/mockData'

import { Navbar } from './components/Navbar'
import { HeroBanner } from './components/HeroBanner'
import { ExecutiveOverview } from './components/ExecutiveOverview'
import { DeliveryDrivers } from './components/DeliveryDrivers'
import { FleetAnalytics } from './components/FleetAnalytics'
import { AIPredictor } from './components/AIPredictor'
import { DataExplorer } from './components/DataExplorer'
import { StrategicDecisions } from './components/StrategicDecisions'
import { RefreshCw, Database, Sparkles, BookOpen, Layers } from 'lucide-react'

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('overview')
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [isLive, setIsLive] = useState<boolean>(false)

  // Dataset states initialized with authentic verified mocks
  const [kpis, setKpis] = useState<KPIs>(mockKPIs)
  const [cityData, setCityData] = useState<CityMetric[]>(mockCityData)
  const [weatherData, setWeatherData] = useState<WeatherMetric[]>(mockWeatherData)
  const [trafficData, setTrafficData] = useState<TrafficMetric[]>(mockTrafficData)
  const [vehicleData, setVehicleData] = useState<VehicleMetric[]>(mockVehicleData)
  const [festivalData, setFestivalData] = useState<FestivalMetric[]>(mockFestivalData)
  const [hourlyData, setHourlyData] = useState<HourlyMetric[]>(mockHourlyData)
  const [partnerAnalysis, setPartnerAnalysis] = useState<PartnerAnalysis>(mockPartnerAnalysis)
  const [topCombinations, setTopCombinations] = useState<TopCombinations>(mockTopCombinations)
  const [decisions, setDecisions] = useState<DecisionItem[]>(mockDecisions)

  const loadAllData = useCallback(async () => {
    setIsLoading(true)
    try {
      const [
        kpisRes,
        cityRes,
        weatherRes,
        trafficRes,
        vehicleRes,
        festRes,
        hourRes,
        partnerRes,
        combRes,
        decRes,
      ] = await Promise.all([
        fetchKPIs(),
        fetchCityData(),
        fetchWeatherData(),
        fetchTrafficData(),
        fetchVehicleData(),
        fetchFestivalData(),
        fetchHourlyData(),
        fetchPartnerAnalysis(),
        fetchTopCombinations(),
        fetchDecisions(),
      ])

      setKpis(kpisRes.data)
      setCityData(cityRes.data)
      setWeatherData(weatherRes.data)
      setTrafficData(trafficRes.data)
      setVehicleData(vehicleRes.data)
      setFestivalData(festRes.data)
      setHourlyData(hourRes.data)
      setPartnerAnalysis(partnerRes.data)
      setTopCombinations(combRes.data)
      setDecisions(decRes.data)

      // If at least one endpoint was live, mark backend connected
      const anyLive = [
        kpisRes.isLive,
        cityRes.isLive,
        weatherRes.isLive,
        trafficRes.isLive,
      ].some(Boolean)

      setIsLive(anyLive)
    } catch (err) {
      console.warn('Backend API connection warning, using FoDS verified dataset:', err)
      setIsLive(false)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    loadAllData()
  }, [loadAllData])

  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 flex flex-col font-sans selection:bg-rose-500 selection:text-white">
      {/* Navigation Bar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        isLive={isLive}
        isLoading={isLoading}
        onRefresh={loadAllData}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        
        {/* Hero banner shown on overview tab */}
        {activeTab === 'overview' && (
          <HeroBanner
            onExploreDrivers={() => setActiveTab('drivers')}
            onOpenPredictor={() => setActiveTab('predictor')}
          />
        )}

        {/* Tab Views */}
        <div className="transition-all duration-300">
          {activeTab === 'overview' && (
            <ExecutiveOverview
              kpis={kpis}
              cityData={cityData}
              weatherData={weatherData}
              trafficData={trafficData}
            />
          )}

          {activeTab === 'drivers' && (
            <DeliveryDrivers
              hourlyData={hourlyData}
              weatherData={weatherData}
              festivalData={festivalData}
              topCombinations={topCombinations}
            />
          )}

          {activeTab === 'fleet' && (
            <FleetAnalytics
              vehicleData={vehicleData}
              partnerAnalysis={partnerAnalysis}
            />
          )}

          {activeTab === 'predictor' && <AIPredictor />}

          {activeTab === 'explorer' && <DataExplorer />}

          {activeTab === 'decisions' && <StrategicDecisions decisions={decisions} />}
        </div>
      </main>

      {/* Modern Academic Footer */}
      <footer className="mt-16 border-t border-slate-800/80 bg-slate-950/60 py-8 px-4 sm:px-8 text-xs text-slate-400">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-7 h-7 rounded-lg bg-rose-600 flex items-center justify-center font-bold text-white text-sm">
              Z
            </div>
            <div>
              <p className="font-semibold text-slate-200">
                Foundation of Data Science (FoDS - 23CSE351) Case Study
              </p>
              <p className="text-[11px] text-slate-500">
                Empirical Logistics & Delivery Optimization Analysis • 45,584 Records
              </p>
            </div>
          </div>

          <div className="flex items-center gap-6 text-[11px]">
            <span className="flex items-center gap-1.5 text-slate-400">
              <Database className="w-3.5 h-3.5 text-rose-400" />
              Dataset: 45,584 Rows
            </span>
            <span className="flex items-center gap-1.5 text-slate-400">
              <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
              Random Forest (API): R² = 0.816
            </span>
            <span className="flex items-center gap-1.5 text-slate-400">
              <BookOpen className="w-3.5 h-3.5 text-emerald-400" />
              CLT Z-Tests & Permutation Resampling
            </span>
          </div>
        </div>
      </footer>
    </div>
  )
}
export default App
