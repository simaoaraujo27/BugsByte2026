const MAX_HISTORY_ITEMS = 100;

function getHistoryKey() {
  const userId = localStorage.getItem('user_id') || 'guest';
  return `recipe_history_${userId}`;
}

export function loadRecipeHistory() {
  try {
    const raw = localStorage.getItem(getHistoryKey());
    const parsed = raw ? JSON.parse(raw) : [];
    if (!Array.isArray(parsed)) return [];
    return parsed.sort((a, b) => (b.created_at || '').localeCompare(a.created_at || ''));
  } catch {
    return [];
  }
}

export function addRecipeToHistory(entry) {
  if (!entry?.name || !entry?.instructions) return;

  const current = loadRecipeHistory();
  const normalized = {
    id: `${Date.now()}-${Math.random().toString(16).slice(2, 8)}`,
    name: entry.name,
    ingredients: Array.isArray(entry.ingredients) ? entry.ingredients : [],
    instructions: Array.isArray(entry.instructions) ? entry.instructions : [],
    calories: entry.calories ?? null,
    source: entry.source || 'sugestao',
    note: entry.note || '',
    created_at: new Date().toISOString()
  };

  const next = [normalized, ...current].slice(0, MAX_HISTORY_ITEMS);
  localStorage.setItem(getHistoryKey(), JSON.stringify(next));
}

export function removeRecipeFromHistory(id) {
  const next = loadRecipeHistory().filter((item) => item.id !== id);
  localStorage.setItem(getHistoryKey(), JSON.stringify(next));
}

export function clearRecipeHistory() {
  localStorage.removeItem(getHistoryKey());
}
