import { useEffect, useRef, useState } from 'react'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { cn } from '@/utils'

type Enemy = { id: number; x: number; y: number; hp: number; speed: number }
type Spike = { id: number; x1: number; y1: number; x2: number; y2: number }

export default function GamesEgg() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const [running, setRunning] = useState(true)
  const [coins, setCoins] = useState(50)
  const [wave, setWave] = useState(1)
  const [eggHp, setEggHp] = useState(100)
  const [cooldown, setCooldown] = useState(0)
  const spikesRef = useRef<Spike[]>([])
  const enemiesRef = useRef<Enemy[]>([])
  const nextId = useRef(1)
  const lastTs = useRef(0)

  useEffect(() => {
    const canvas = canvasRef.current!
    const ctx = canvas.getContext('2d')!
    let raf = 0

    function spawnWave(n: number) {
      const width = canvas.width
      for (let i = 0; i < n; i++) {
        enemiesRef.current.push({
          id: nextId.current++,
          x: Math.random() * width,
          y: -Math.random() * 200 - 20,
          hp: 20 + wave * 5,
          speed: 30 + Math.random() * 20 + wave * 2,
        })
      }
    }

    function collideSegmentPoint(sp: Spike, x: number, y: number): boolean {
      const { x1, y1, x2, y2 } = sp
      const A = x - x1
      const B = y - y1
      const C = x2 - x1
      const D = y2 - y1
      const dot = A * C + B * D
      const lenSq = C * C + D * D
      let param = -1
      if (lenSq !== 0) param = dot / lenSq
      let xx, yy
      if (param < 0) { xx = x1; yy = y1 } else if (param > 1) { xx = x2; yy = y2 } else { xx = x1 + param * C; yy = y1 + param * D }
      const dx = x - xx
      const dy = y - yy
      const dist = Math.sqrt(dx * dx + dy * dy)
      return dist < 8
    }

    function step(ts: number) {
      const dt = Math.min(0.05, (ts - lastTs.current) / 1000 || 0.016)
      lastTs.current = ts
      const w = canvas.width
      const h = canvas.height
      ctx.clearRect(0, 0, w, h)

      // background
      ctx.fillStyle = '#0b1220'
      ctx.fillRect(0, 0, w, h)

      // egg (target) bottom center
      const eggX = w / 2
      const eggY = h - 60
      ctx.beginPath()
      ctx.ellipse(eggX, eggY, 28, 36, 0, 0, Math.PI * 2)
      ctx.fillStyle = '#fde68a'
      ctx.fill()
      ctx.strokeStyle = '#f59e0b'
      ctx.stroke()

      // egg health bar
      ctx.fillStyle = '#1e293b'
      ctx.fillRect(eggX - 40, eggY + 40, 80, 6)
      ctx.fillStyle = '#10b981'
      ctx.fillRect(eggX - 40, eggY + 40, Math.max(0, Math.min(80, (eggHp / 100) * 80)), 6)

      // passive pulse (cooldown visual)
      if (cooldown > 0) {
        ctx.beginPath()
        ctx.arc(eggX, eggY, 50 + (1 - cooldown) * 20, 0, Math.PI * 2)
        ctx.strokeStyle = 'rgba(56,189,248,0.3)'
        ctx.stroke()
      }

      // spikes
      ctx.strokeStyle = '#94a3b8'
      ctx.lineWidth = 3
      for (const sp of spikesRef.current) {
        ctx.beginPath()
        ctx.moveTo(sp.x1, sp.y1)
        ctx.lineTo(sp.x2, sp.y2)
        ctx.stroke()
      }

      // enemies
      const alive: Enemy[] = []
      for (const e of enemiesRef.current) {
        const ny = e.y + e.speed * dt
        let nhp = e.hp
        // collision with spikes
        for (const sp of spikesRef.current) {
          if (collideSegmentPoint(sp, e.x, ny)) {
            nhp -= 30 * dt
          }
        }
        // reach egg
        const dx = e.x - eggX
        const dy = ny - eggY
        if (Math.hypot(dx, dy) < 34) {
          const dmg = 10 * dt
          setEggHp((v) => Math.max(0, v - dmg))
          continue
        }
        // render
        ctx.beginPath()
        ctx.arc(e.x, ny, 8, 0, Math.PI * 2)
        ctx.fillStyle = '#ef4444'
        ctx.fill()
        if (nhp > 0) alive.push({ ...e, y: ny, hp: nhp })
      }
      enemiesRef.current = alive

      // passive pulse damage to nearby enemies on cooldown end
      if (cooldown <= 0) {
        for (const e of enemiesRef.current) {
          const d = Math.hypot(e.x - eggX, e.y - eggY)
          if (d < 60) e.hp -= 20
        }
        setCooldown(1)
      } else {
        setCooldown((c) => Math.max(0, c - dt * 0.2))
      }

      // wave/coins
      if (enemiesRef.current.length === 0) {
        setCoins((c) => c + 10 + wave * 2)
        setWave((wvv) => wvv + 1)
        spawnWave(4 + wave)
      }

      if (running && eggHp > 0) raf = requestAnimationFrame(step)
    }

    // init
    canvas.width = Math.min(800, window.innerWidth)
    canvas.height = Math.min(600, Math.floor(window.innerHeight * 0.8))
    spawnWave(5)
    raf = requestAnimationFrame(step)

    return () => cancelAnimationFrame(raf)
  }, [running, wave, eggHp, cooldown])

  // gesture: swipe to place spike
  useEffect(() => {
    const canvas = canvasRef.current!
    let sx = 0, sy = 0, dragging = false
    function pt(e: MouseEvent | TouchEvent) {
      const rect = canvas.getBoundingClientRect()
      const x = 'touches' in e ? e.touches[0].clientX : (e as MouseEvent).clientX
      const y = 'touches' in e ? e.touches[0].clientY : (e as MouseEvent).clientY
      return { x: x - rect.left, y: y - rect.top }
    }
    function down(e: any) { dragging = true; const p = pt(e); sx = p.x; sy = p.y }
    function up(e: any) {
      if (!dragging) return
      dragging = false
      const p = pt(e)
      // cost 15
      if (coins >= 15) {
        spikesRef.current.push({ id: Date.now(), x1: sx, y1: sy, x2: p.x, y2: p.y })
        setCoins((c) => c - 15)
      }
    }
    canvas.addEventListener('mousedown', down)
    canvas.addEventListener('touchstart', down)
    window.addEventListener('mouseup', up)
    window.addEventListener('touchend', up)
    return () => {
      canvas.removeEventListener('mousedown', down)
      canvas.removeEventListener('touchstart', down)
      window.removeEventListener('mouseup', up)
      window.removeEventListener('touchend', up)
    }
  }, [coins])

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Egg Defender (prototype)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between text-sm text-slate-300 mb-2">
            <div>Волна: <span className="font-semibold">{wave}</span></div>
            <div>Монеты: <span className="font-semibold">{coins}</span></div>
            <div>HP яйца: <span className="font-semibold">{Math.round(eggHp)}</span></div>
          </div>
          <canvas ref={canvasRef} className="w-full rounded-lg border border-border bg-surface" />
          <div className="mt-3 flex gap-2">
            <Button onClick={() => setRunning((r) => !r)} variant="secondary">{running ? 'Пауза' : 'Продолжить'}</Button>
            <Button onClick={() => { spikesRef.current = []; enemiesRef.current = []; setWave(1); setCoins(50); setEggHp(100) }}>Рестарт</Button>
          </div>
          <p className="mt-2 text-xs text-slate-400">Свайпните по полю, чтобы поставить заграждение (15 монет). Яйцо пульсирует волной урона по перезарядке.</p>
        </CardContent>
      </Card>
    </div>
  )
}


