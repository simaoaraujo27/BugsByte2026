/**
 * Utilitário para formatar e exportar listas de compras
 */

const categories = {
  fruta: ['maçã', 'banana', 'laranja', 'limão', 'pêra', 'uvas', 'morangos'],
  vegetais: ['alface', 'tomate', 'cebola', 'alho', 'brócolos', 'cenoura', 'espinafres', 'couve', 'pimento'],
  proteina: ['frango', 'carne', 'peixe', 'ovos', 'tofu', 'salmão', 'peru'],
  laticinios: ['leite', 'queijo', 'iogurte', 'manteiga', 'natas'],
  despensa: ['arroz', 'massa', 'azeite', 'sal', 'açúcar', 'farinha', 'feijão', 'grão']
};

function categorizeIngredient(ingredient) {
  const lower = ingredient.toLowerCase();
  for (const [cat, items] of Object.entries(categories)) {
    if (items.some(item => lower.includes(item))) return cat.toUpperCase();
  }
  return 'OUTROS';
}

export function formatShoppingList(ingredients, recipeName = '') {
  if (!ingredients || ingredients.length === 0) return '';

  const grouped = {};
  ingredients.forEach(ing => {
    const cat = categorizeIngredient(ing);
    if (!grouped[cat]) grouped[cat] = [];
    grouped[cat].push(ing);
  });

  let text = `🛒 *Lista de Compras: ${recipeName || 'NutriVentures'}*\n\n`;
  
  for (const [cat, items] of Object.entries(grouped)) {
    text += `*${cat}*
`;
    items.forEach(item => {
      text += `[ ] ${item}\n`;
    });
    text += '\n';
  }

  text += 'Gerado por *NutriVentures* 🥗';
  return text;
}

export function shareToWhatsApp(text) {
  const url = `https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`;
  window.open(url, '_blank');
}

export async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    console.error('Erro ao copiar:', err);
    return false;
  }
}
