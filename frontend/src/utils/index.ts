// Совместимый слой утилит, замещающий '@/lib/utils'

export function cn(...classes: Array<string | undefined | false | null>): string {
  return classes.filter(Boolean).join(' ');
}

export function getStoredUserId(): string {
  if (typeof localStorage === 'undefined') return 'default_user';
  return localStorage.getItem('user_id') || 'default_user';
}

export function setStoredUserId(userId: string): void {
  try {
    localStorage.setItem('user_id', userId);
  } catch {}
}

export function getHealthColor(value: number): string {
  if (value <= 20) return 'health-critical';
  if (value <= 50) return 'health-low';
  return 'health-ok';
}

export function getHealthText(value: number): string {
  if (value <= 0) return 'Питомец мертв';
  if (value <= 20) return 'Критическое здоровье';
  if (value <= 50) return 'Нужна забота';
  return 'Чувствует себя нормально';
}

type StageKey = 'egg' | 'baby' | 'adult' | string;
export function getStageInfo(stage: StageKey): { name: string; description: string; emoji: string; color: string } {
  switch (stage) {
    case 'egg':
      return { name: 'Яйцо', description: 'Забота и тепло помогут', emoji: '🥚', color: 'from-blue-300 to-blue-500 bg-gradient-to-r' };
    case 'baby':
      return { name: 'Детеныш', description: 'Кормление и уход важны', emoji: '🍼', color: 'from-emerald-300 to-emerald-500 bg-gradient-to-r' };
    case 'adult':
      return { name: 'Взрослый', description: 'Нужны развлечения', emoji: '🦴', color: 'from-purple-300 to-purple-500 bg-gradient-to-r' };
    default:
      return { name: 'Неизвестно', description: 'Стадия не распознана', emoji: '❓', color: 'from-slate-300 to-slate-500 bg-gradient-to-r' };
  }
}

export function formatTime(totalSeconds: number): string {
  const s = Math.max(0, Math.floor(totalSeconds));
  const m = Math.floor(s / 60);
  const sec = s % 60;
  return `${m}:${sec.toString().padStart(2, '0')}`;
}

export function formatDate(iso?: string): string {
  if (!iso) return '';
  try {
    const d = new Date(iso);
    return d.toLocaleString();
  } catch {
    return iso;
  }
}

export function getActionCost(stage: StageKey): number {
  // Базовые стоимости, синхронизировать при необходимости с backend/config/settings.py ACTION_COSTS
  if (stage === 'egg') return 5;
  if (stage === 'baby') return 10;
  if (stage === 'adult') return 20;
  return 10;
}


