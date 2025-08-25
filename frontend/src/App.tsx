import { Routes, Route } from 'react-router-dom'
import { Suspense, lazy } from 'react'
import Layout from './components/Layout'
import LoadingSpinner from './components/ui/LoadingSpinner'
import FontLoader from './components/ui/FontLoader'

// Lazy load components
const Home = lazy(() => import('./pages/Home'))
const PetDetails = lazy(() => import('./pages/PetDetails'))
const Economy = lazy(() => import('./pages/Economy'))
const History = lazy(() => import('./pages/History'))
const Admin = lazy(() => import('./pages/Admin'))
const Settings = lazy(() => import('./pages/Settings'))
const ComponentsDemo = lazy(() => import('./pages/Components'))
const GamesRunner = lazy(() => import('./pages/GamesRunner'))
const GamesPuzzle = lazy(() => import('./pages/GamesPuzzle'))
const GamesMatch3 = lazy(() => import('./pages/GamesMatch3'))
const GamesEgg = lazy(() => import('./pages/GamesEgg'))
const Market = lazy(() => import('./pages/Market'))

function App() {
  return (
    <FontLoader>
      <Layout>
        <Suspense fallback={<LoadingSpinner />}>
          <Routes>
            {/* Админка/для разработчика */}
            <Route path="/" element={<Home />} />
            <Route path="/pet/:petId" element={<PetDetails />} />
            <Route path="/economy" element={<Economy />} />
            <Route path="/history" element={<History />} />
            <Route path="/market" element={<Market />} />
            <Route path="/admin" element={<Admin />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/components" element={<ComponentsDemo />} />
            <Route path="/games/runner" element={<GamesRunner />} />
            <Route path="/games/puzzle" element={<GamesPuzzle />} />
            <Route path="/games/match3" element={<GamesMatch3 />} />
            {/* скрытый маршрут прототипа Egg Defender */}
            <Route path="/games/egg" element={<GamesEgg />} />
          </Routes>
        </Suspense>
      </Layout>
    </FontLoader>
  )
}

export default App 