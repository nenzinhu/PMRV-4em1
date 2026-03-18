const fs = require('fs');
const path = require('path');

function parseCsv(text) {
  const rows = [];
  let row = [];
  let cell = '';
  let quoted = false;

  for (let i = 0; i < text.length; i++) {
    const char = text[i];
    const next = text[i + 1];

    if (char === '"') {
      if (quoted && next === '"') {
        cell += '"';
        i++;
      } else {
        quoted = !quoted;
      }
      continue;
    }

    if (char === ',' && !quoted) {
      row.push(cell);
      cell = '';
      continue;
    }

    if ((char === '\n' || char === '\r') && !quoted) {
      if (char === '\r' && next === '\n') i++;
      row.push(cell);
      if (row.some(function (item) { return item.trim() !== ''; })) rows.push(row);
      row = [];
      cell = '';
      continue;
    }

    cell += char;
  }

  if (cell.length || row.length) {
    row.push(cell);
    if (row.some(function (item) { return item.trim() !== ''; })) rows.push(row);
  }

  return rows;
}

function csvEscape(value) {
  const text = String(value || '');
  if (/[",\r\n]/.test(text)) return '"' + text.replace(/"/g, '""') + '"';
  return text;
}

function safeText(value) {
  return String(value || '').trim();
}

function normalizeHeader(value) {
  return safeText(value)
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, ' ')
    .trim();
}

function normalizeCategory(value) {
  const normalized = normalizeHeader(value);
  if (!normalized) return 'Sem categoria';
  if (normalized.includes('gravissima') || normalized.includes('graviss')) return 'Gravíssima';
  if (normalized.includes('grave')) return 'Grave';
  if (normalized.includes('media')) return 'Média';
  if (normalized.includes('leve')) return 'Leve';
  return 'Sem categoria';
}

function looksLikeScope(value) {
  return /(rodov|municipal|estad|federal)/i.test(value || '');
}

function looksLikeCategoryPart(value) {
  const normalized = normalizeHeader(value);
  if (!normalized) return false;
  if (normalized === 'o' || normalized === '0') return false;
  if (/(leve|grave|graviss|gravissima|media)/.test(normalized)) return true;
  if (/^[0-9o]+$/.test(normalized)) return true;
  if (/^[0-9o]+\s*$/.test(normalized)) return true;
  if (/^[0-9o]+\s*$/.test(normalized.replace(/-/g, '').trim())) return true;
  if (/^[0-9o]+\s*$/.test(normalized.replace(/x/g, '').trim())) return true;
  if (/^[0-9o]+\s*$/.test(normalized.replace(/[a-z]/g, '').trim())) return true;
  if (/^[0-9o]+\s*$/.test(normalized.replace(/\s+/g, ''))) return true;
  return /^[0-9o]+\s*[-x]*\s*$/.test(normalized);
}

function extractCategory(cells, endIndex, startIndex) {
  const parts = [];
  let cursor = endIndex;

  while (cursor >= startIndex && parts.length < 3) {
    const value = cells[cursor];
    if (!looksLikeCategoryPart(value)) break;
    parts.unshift(value);
    cursor--;
  }

  if (!parts.length && cursor >= startIndex) {
    parts.unshift(cells[cursor]);
    cursor--;
  }

  return {
    categoria: normalizeCategory(parts.join(' ')),
    nextIndex: cursor
  };
}

function cleanRow(row) {
  const cells = row.map(safeText).filter(Boolean);
  if (!cells.length) return null;
  if (!/^\d{4,5}(?:-\d+)?$/.test(cells[0])) return null;

  let startIndex = 1;
  if (cells[startIndex] && /^[a-z0-9]{1,2}$/i.test(cells[startIndex]) && cells[startIndex].toLowerCase() === 'o') {
    startIndex++;
  }

  let endIndex = cells.length - 1;
  let abrangencia = '';
  if (looksLikeScope(cells[endIndex])) {
    abrangencia = cells[endIndex];
    endIndex--;
  }

  const categoryInfo = extractCategory(cells, endIndex, startIndex);
  endIndex = categoryInfo.nextIndex;

  const infrator = endIndex >= startIndex ? cells[endIndex] : '';
  const artigo = endIndex - 1 >= startIndex ? cells[endIndex - 1] : '';
  const descricaoStart = startIndex;
  const descricaoEnd = Math.max(descricaoStart, endIndex - 2);
  const descricao = cells.slice(descricaoStart, descricaoEnd + 1).join(' ').trim();

  return {
    codigo: cells[0],
    descricao: descricao,
    artigo: artigo,
    infrator: infrator,
    categoria: categoryInfo.categoria,
    abrangencia: abrangencia
  };
}

function main() {
  const projectRoot = __dirname;
  const inputPath = path.join(projectRoot, 'fish.csv');
  const outputPath = path.join(projectRoot, 'fish.cleaned.csv');
  const shouldOverwrite = process.argv.includes('--write');

  const content = fs.readFileSync(inputPath, 'utf8');
  const rows = parseCsv(content);

  const cleaned = rows
    .map(cleanRow)
    .filter(Boolean)
    .map(function (row) {
      return [
        row.codigo,
        row.descricao,
        row.artigo,
        row.infrator,
        row.categoria,
        row.abrangencia
      ].map(csvEscape).join(',');
    })
    .join('\r\n') + '\r\n';

  fs.writeFileSync(outputPath, cleaned, 'utf8');

  if (shouldOverwrite) {
    fs.copyFileSync(outputPath, inputPath);
  }

  console.log('Arquivo gerado:', outputPath);
  if (shouldOverwrite) {
    console.log('Arquivo original atualizado:', inputPath);
  } else {
    console.log('Use --write para sobrescrever o fish.csv.');
  }
}

main();
