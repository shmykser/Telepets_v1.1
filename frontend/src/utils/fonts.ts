/* Утилиты шрифтов: проверка доступности и применение fallback. */

const SYSTEM_FALLBACK = (
  'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, ' +
  'Helvetica, Arial, "Noto Sans", Ubuntu, Cantarell, sans-serif'
);

const PREFERRED_FONTS = [
  'Inter',
  'Poppins',
  'Segoe UI',
  'Roboto',
  'Helvetica',
  'Arial',
];

function isFontAvailableCSS(fontFamily: string): boolean {
  try {
    // @ts-ignore
    if (typeof document !== 'undefined' && (document as any).fonts?.check) {
      const quoted = fontFamily.includes(' ') ? `"${fontFamily}"` : fontFamily;
      // 12px достаточно для проверки
      return (document as any).fonts.check(`12px ${quoted}`) === true;
    }
  } catch (_) {}
  return false;
}

function isFontAvailableCanvas(fontFamily: string): boolean {
  try {
    if (typeof document === 'undefined') return false;
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    if (!ctx) return false;
    const sample = 'abcdefghiABCDEFGHI_0123456789';
    ctx.font = '16px monospace';
    const baseline = ctx.measureText(sample).width;
    const quoted = fontFamily.includes(' ') ? `"${fontFamily}"` : fontFamily;
    ctx.font = `16px ${quoted}, monospace`;
    const width = ctx.measureText(sample).width;
    return width !== baseline;
  } catch (_) {
    return false;
  }
}

export function isFontAvailable(fontFamily: string): boolean {
  return isFontAvailableCSS(fontFamily) || isFontAvailableCanvas(fontFamily);
}

export function getAvailableFont(_variant?: string): string {
  for (const f of PREFERRED_FONTS) {
    if (isFontAvailable(f)) return f;
  }
  return SYSTEM_FALLBACK;
}

export function applyFontFallbacks(fontFamily: string): void {
  try {
    if (typeof document === 'undefined') return;
    const family = fontFamily || SYSTEM_FALLBACK;
    document.documentElement.style.setProperty('--app-font', family);
    if (document.body) document.body.style.fontFamily = 'var(--app-font)';
  } catch (_) {}
}

export async function initializeFonts(): Promise<void> {
  try {
    const chosen = getAvailableFont();
    applyFontFallbacks(chosen);
  } catch (_) {
    applyFontFallbacks(SYSTEM_FALLBACK);
  }
}


