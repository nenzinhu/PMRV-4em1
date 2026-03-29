/* ---------------------------------------------------------------
   THUMBS DAS ABAS — copia src das imagens v360 para os thumbnails
--------------------------------------------------------------- */
document.addEventListener('DOMContentLoaded', function(){
  const map = {
    'dan-thumb-frente':   'v360-img-frente',
    'dan-thumb-tras':     'v360-img-tras',
    'dan-thumb-direita':  'v360-img-direita',
    'dan-thumb-esquerda': 'v360-img-esquerda'
  };
  Object.keys(map).forEach(function(thumbId){
    const src = document.getElementById(map[thumbId]);
    const thumb = document.getElementById(thumbId);
    if (src && thumb) thumb.src = src.src;
  });
  bindDeclarativeHandlers();
  registerServiceWorker();
});

/* ---------------------------------------------------------------
   NAVEGAÇÃO
--------------------------------------------------------------- */
const SCREENS = ['home','assumir','envolvidos','pmrv','danos','relatorio','infracoes','help','ended','docs'];

function go(name) {
  SCREENS.forEach(id => {
    const el = document.getElementById('screen-' + id);
    if (el) el.classList.toggle('active', id === name);
  });
  const app = document.querySelector('.app');
  if (app) app.classList.toggle('app-wide', name === 'infracoes');
  window.scrollTo({ top: 0, behavior: 'smooth' });

  // Inicializar telas que precisam de setup
  if (name === 'envolvidos' && document.getElementById('env_lista').children.length === 0) env_adicionar();
  if (name === 'danos') {
    danPrepararTela();
  }
  if (name === 'pmrv') { pmrv_verificarRodovia(); pmrv_mudarSubtipo(); pmrv_atualizar(); }
  if (name === 'relatorio') {
    document.getElementById('rel-count-env').textContent = document.querySelectorAll('#env_lista .person-card').length || '0';
    document.getElementById('rel-count-dan').textContent = danVeiculosSalvos.length || '0';
    document.getElementById('rel-result-area').style.display = 'none';
  }
  if (name === 'infracoes' && typeof window.infra_init === 'function') {
    window.infra_init();
  }
}

/* ---------------------------------------------------------------
   UTILITÁRIOS COMPARTILHADOS
--------------------------------------------------------------- */
function capFirst(input) {
  const v = input.value;
  if (v.length > 0) input.value = v.charAt(0).toUpperCase() + v.slice(1).toLowerCase();
}

function copiar(elId, btn) {
  const texto = document.getElementById(elId).textContent;
  navigator.clipboard.writeText(texto).then(() => {
    const original = btn.innerHTML;
    btn.innerHTML = '✅ Copiado!';
    btn.classList.add('btn-success');
    setTimeout(() => { btn.innerHTML = original; }, 2000);
  });
}

function whatsapp(elId) {
  const texto = document.getElementById(elId).textContent;
  window.open('https://wa.me/?text=' + encodeURIComponent(texto), '_blank');
}

function mascaraTelefone(input) {
  let v = input.value.replace(/\D/g, '');
  if (v.length > 10) v = v.replace(/^(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
  else                v = v.replace(/^(\d{2})(\d{4})(\d{0,4})/, '($1) $2-$3');
  input.value = v;
}

function registerServiceWorker() {
  if (!('serviceWorker' in navigator)) return;
  window.addEventListener('load', function() {
    navigator.serviceWorker.register('./service_worker.js').catch(function() {});
  }, { once: true });
}

function bindDeclarativeHandlers() {
  document.addEventListener('click', function(event) {
    dispatchDeclarativeEvent(event, 'data-click');
  });

  document.addEventListener('change', function(event) {
    dispatchDeclarativeEvent(event, 'data-change');
  });

  document.addEventListener('input', function(event) {
    dispatchDeclarativeEvent(event, 'data-input');
  });

  document.addEventListener('keydown', function(event) {
    const el = event.target.closest('[data-keydown-enter]');
    if (!el || event.key !== 'Enter') return;
    invokeDeclarativeExpression(el.getAttribute('data-keydown-enter'), el, event);
  });

  document.addEventListener('pointerdown', function(event) {
    dispatchDeclarativeEvent(event, 'data-pointerdown');
  });
}

function dispatchDeclarativeEvent(event, attrName) {
  const el = event.target.closest('[' + attrName + ']');
  if (!el) return;
  event.declarativeTarget = el;
  invokeDeclarativeExpression(el.getAttribute(attrName), el, event);
}

function invokeDeclarativeExpression(expr, el, event) {
  if (!expr) return;
  const match = expr.trim().match(/^([A-Za-z_$][\w$]*)\((.*)\)$/);
  if (!match) return;

  const fn = window[match[1]];
  if (typeof fn !== 'function') return;

  const args = parseDeclarativeArgs(match[2], el, event);
  fn.apply(window, args);
}

function parseDeclarativeArgs(rawArgs, el, event) {
  const args = [];
  let current = '';
  let quote = null;

  for (let i = 0; i < rawArgs.length; i++) {
    const ch = rawArgs[i];
    const prev = rawArgs[i - 1];

    if (quote) {
      current += ch;
      if (ch === quote && prev !== '\\') quote = null;
      continue;
    }

    if (ch === '\'' || ch === '"') {
      quote = ch;
      current += ch;
      continue;
    }

    if (ch === ',') {
      args.push(resolveDeclarativeToken(current.trim(), el, event));
      current = '';
      continue;
    }

    current += ch;
  }

  if (current.trim() || rawArgs.trim()) {
    args.push(resolveDeclarativeToken(current.trim(), el, event));
  }

  return args;
}

function resolveDeclarativeToken(token, el, event) {
  if (token === '' || token === 'undefined') return undefined;
  if (token === 'this') return el;
  if (token === 'event') return event;
  if (token === 'true') return true;
  if (token === 'false') return false;
  if (token === 'null') return null;
  if (/^-?\d+(\.\d+)?$/.test(token)) return Number(token);

  const quoted = token.match(/^(['"])(.*)\1$/);
  if (quoted) {
    return quoted[2]
      .replace(/\\'/g, '\'')
      .replace(/\\"/g, '"')
      .replace(/\\\\/g, '\\');
  }

  return token;
}


/**
 * Limpa todos os dados de cache do navegador para o aplicativo.
 * Remove LocalStorage, SessionStorage e forca a limpeza do Service Worker (PWA).
 */
function core_limparCache() {
    if (confirm('Atenção!\n\nEsta ação limpará todos os dados salvos temporariamente no aplicativo e forçará a atualização para a versão mais recente.\n\nDeseja continuar?')) {
        
        // 1. Limpa o Storage do navegador
        localStorage.clear();
        sessionStorage.clear();
        
        // 2. Tenta limpar os caches do Service Worker (PWA)
        if ('caches' in window) {
            caches.keys().then(names => {
                for (let name of names) caches.delete(name);
            });
        }
        
        // 3. Unregister todos os Service Workers para forçar atualização
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.getRegistrations().then(registrations => {
                for (let registration of registrations) {
                    registration.unregister();
                }
            });
        }

        // 4. Feedback e Recarregamento
        alert('Cache limpo com sucesso!\nO aplicativo será reiniciado.');
        window.location.reload(true);
    }
}

