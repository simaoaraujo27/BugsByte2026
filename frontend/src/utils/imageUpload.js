const DEFAULT_MAX_BYTES = 900 * 1024;
const DEFAULT_MAX_DIMENSION = 1400;

function readImage(file) {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file);
    const img = new Image();
    img.onload = () => {
      URL.revokeObjectURL(url);
      resolve(img);
    };
    img.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new Error('Não foi possível ler a imagem.'));
    };
    img.src = url;
  });
}

function canvasToBlob(canvas, quality) {
  return new Promise((resolve, reject) => {
    canvas.toBlob(
      (blob) => {
        if (!blob) {
          reject(new Error('Falha ao comprimir imagem.'));
          return;
        }
        resolve(blob);
      },
      'image/jpeg',
      quality
    );
  });
}

export async function optimizeImageForVision(file, options = {}) {
  if (!file || !file.type?.startsWith('image/')) {
    return file;
  }

  const maxBytes = options.maxBytes ?? DEFAULT_MAX_BYTES;
  const maxDimension = options.maxDimension ?? DEFAULT_MAX_DIMENSION;

  // Already small enough and already JPEG.
  if (file.size <= maxBytes && file.type === 'image/jpeg') {
    return file;
  }

  const image = await readImage(file);
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  if (!ctx) {
    return file;
  }

  let scale = Math.min(1, maxDimension / Math.max(image.width, image.height));
  let width = Math.max(1, Math.round(image.width * scale));
  let height = Math.max(1, Math.round(image.height * scale));

  let bestBlob = null;
  let quality = 0.86;

  for (let attempt = 0; attempt < 8; attempt += 1) {
    canvas.width = width;
    canvas.height = height;
    ctx.clearRect(0, 0, width, height);
    ctx.drawImage(image, 0, 0, width, height);

    const blob = await canvasToBlob(canvas, quality);
    bestBlob = blob;
    if (blob.size <= maxBytes) {
      break;
    }

    if (quality > 0.58) {
      quality -= 0.08;
    } else {
      width = Math.max(700, Math.round(width * 0.85));
      height = Math.max(700, Math.round(height * 0.85));
    }
  }

  if (!bestBlob) {
    return file;
  }

  const outputName = file.name.replace(/\.[^/.]+$/, '') + '.jpg';
  return new File([bestBlob], outputName, { type: 'image/jpeg' });
}
