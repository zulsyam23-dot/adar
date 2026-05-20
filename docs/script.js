let pyodide = null;
let pyodideReady = false;

// Code tabs
document.querySelectorAll('.code-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.code-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.code-panel').forEach(p => p.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById('code-' + tab.dataset.tab).classList.add('active');
  });
});

// Pyodide
async function initPyodide() {
  const loading = document.getElementById('loading-indicator');
  const error = document.getElementById('error-display');
  loading.classList.remove('hidden');

  try {
    pyodide = await loadPyodide({
      indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.27.4/full/',
    });

    const compilerFiles = await fetchCompilerFiles();
    for (const [path, code] of Object.entries(compilerFiles)) {
      const parts = path.split('/');
      let dir = '';
      for (let i = 0; i < parts.length - 1; i++) {
        dir += '/' + parts[i];
        try { pyodide.FS.mkdir(dir); } catch {}
      }
      pyodide.FS.writeFile(path, code);
    }

    pyodide.runPython(`
      import sys
      sys.path.insert(0, '/compiler')
    `);

    pyodideReady = true;
    loading.innerHTML = '<span class="spinner"></span> Compiler loaded! Click <strong>Compile</strong> to run.';
    setTimeout(() => { loading.classList.add('hidden'); }, 2000);
  } catch (err) {
    error.textContent = 'Failed to load compiler: ' + err.message;
    error.classList.remove('hidden');
    loading.classList.add('hidden');
  }
}

async function fetchCompilerFiles() {
  const files = {};
  const base = '/adar/compiler';

  const knownFiles = [
    '__init__.py', 'cli.py',
    'lexer/__init__.py', 'lexer/lexer.py', 'lexer/token.py',
    'parser/__init__.py', 'parser/parser.py', 'parser/ast.py',
    'checker/__init__.py', 'checker/checker.py', 'checker/css_spec.py',
    'resolver/__init__.py', 'resolver/resolver.py',
    'codegen/__init__.py', 'codegen/codegen.py',
    'optimizer/__init__.py',
    'adarpc/__init__.py',
  ];

  for (const f of knownFiles) {
    const url = `${base}/${f}`;
    try {
      const resp = await fetch(url);
      if (resp.ok) {
        files[`/compiler/${f}`] = await resp.text();
      }
    } catch {}
  }

  return files;
}

async function compile() {
  const input = document.getElementById('input');
  const output = document.getElementById('output');
  const error = document.getElementById('error-display');
  const runBtn = document.getElementById('run-btn');
  error.classList.add('hidden');

  if (!pyodideReady) {
    output.innerHTML = 'Loading compiler, please wait&hellip;';
    if (!pyodide) initPyodide();
    return;
  }

  const source = input.value;
  runBtn.disabled = true;
  runBtn.textContent = 'Compiling...';

  pyodide.FS.writeFile('/tmp/playground.adar', source);

  try {
    const result = pyodide.runPython(`
import json, sys
from adar.lexer import Lexer
from adar.parser import Parser
from adar.checker import Checker, CSSSpec
from adar.resolver import Resolver
from adar.codegen import CodeGenerator

with open('/tmp/playground.adar', 'r') as f:
    source = f.read()

try:
    lexer = Lexer(source, '<playground>')
    tokens = lexer.tokenize()
except SyntaxError as e:
    print(json.dumps({'error': f'Lexer Error: {e}'}))
    sys.exit(0)

try:
    parser = Parser(tokens)
    ast = parser.parse()
except SyntaxError as e:
    print(json.dumps({'error': f'Parser Error: {e}'}))
    sys.exit(0)

spec = CSSSpec()
checker = Checker(spec)
result = checker.check(ast)

if result.errors:
    errs = '\\n'.join(f'Type Error: {e.message}' for e in result.errors)
    print(json.dumps({'error': errs}))
    sys.exit(0)

resolver = Resolver()
resolved = resolver.resolve(ast)

codegen = CodeGenerator(scoped=False, pretty=True, source_file='<playground>')
css = codegen.generate(resolved)

print(json.dumps({'css': css}))
`);
    const data = JSON.parse(result);
    if (data.error) {
      output.innerHTML = data.error;
      output.style.color = '#fca5a5';
    } else {
      output.textContent = data.css;
      output.style.color = '#6ee7b7';
    }
  } catch (err) {
    output.innerHTML = 'Error: ' + err.message;
    output.style.color = '#fca5a5';
  }

  runBtn.disabled = false;
  runBtn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 3l14 9-14 9V3z"/></svg> Compile';
}

function copyOutput() {
  const output = document.getElementById('output');
  navigator.clipboard.writeText(output.textContent).catch(() => {});
}

function resetCode() {
  document.getElementById('input').value = `// Variables
$primary = #3b82f6
$radius = 8px

// Mixin
mixin card-base {
    border-radius: $radius
    padding: 16px
    box-shadow: 0 2px 8px rgba(0,0,0,0.1)
}

// Rule with nesting
.btn {
    include card-base
    background: $primary
    color: white
    border: none
    cursor: pointer

    &:hover {
        background: #2563eb
        transform: translateY(-2px)
    }
}`;
}

window.compile = compile;
window.copyOutput = copyOutput;
window.resetCode = resetCode;

if (document.getElementById('playground')) {
  initPyodide();
}
