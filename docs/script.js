let pyodide = null;
let pyodideReady = false;

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
    loading.textContent = 'Compiler loaded! Click "Compile" to run.';
    setTimeout(() => { loading.classList.add('hidden'); }, 1500);
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
  error.classList.add('hidden');

  if (!pyodideReady) {
    output.textContent = 'Loading compiler... please wait.';
    if (!pyodide) initPyodide();
    return;
  }

  const source = input.value;

  // Write source to virtual filesystem (safe, no escaping issues)
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
      output.textContent = data.error;
      output.style.color = '#fca5a5';
    } else {
      output.textContent = data.css;
      output.style.color = '#6ee7b7';
    }
  } catch (err) {
    output.textContent = 'Error: ' + err.message;
    output.style.color = '#fca5a5';
  }
}

function copyOutput() {
  const output = document.getElementById('output');
  navigator.clipboard.writeText(output.textContent).catch(() => {});
}

window.compile = compile;
window.copyOutput = copyOutput;

if (document.getElementById('playground')) {
  initPyodide();
}
