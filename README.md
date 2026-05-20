<p align="center">
  <h1 align="center">&lt;Adar/&gt;</h1>
  <p align="center">Modern CSS-like styling language with <strong>compile-time type checking</strong></p>
</p>

---

**Adar** is a utility-first styling language that compiles to modular, scoped CSS. It catches CSS property type errors at compile time.

```adar
$primary = #3b82f6
$radius = 8px

.card {
    background: white
    border-radius: $radius
    box-shadow: 0 1px 3px rgba(0,0,0,0.1)

    &:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.15)
    }
}
```

## Quick Start

```bash
pip install -e .

# Compile single file
adar build style.adar -o dist/

# Type-check
adar check style.adar

# Or use adarpc for project management
adarpc init my-site
cd my-site
adarpc build
adarpc serve
```

## Features

| Feature | Description |
|---------|-------------|
| Type checking | Validates 150+ CSS properties at compile time |
| CSS Modules | Automatic class scoping with `.modules.json` mapping |
| Themes | `theme name { }` blocks compile to `[data-theme="name"]` |
| Mixins | Reusable style blocks with parameters |
| Functions | Custom `function name(params) { }` for computed values |
| Nesting | CSS nesting with `&` parent reference |
| if/else | Compile-time conditional branches |
| Media queries | `@media` support with nesting |
| CSS variables | `$var` -> `var(--var)` in output |
| Minification | `--minify` flag for production builds |

## Project Structure

```
adar/
├── adar/                    # Compiler source
│   ├── lexer/               # Tokenizer
│   ├── parser/              # Recursive descent parser
│   ├── checker/             # Type checker
│   ├── resolver/            # Variable/mixin/function resolution
│   ├── codegen/             # CSS code generator
│   ├── adarpc/              # Package manager (init, build, serve, watch)
│   └── cli.py               # CLI entry point
├── docs/guide.md            # Full language documentation
├── examples/                # Example .adar files
├── tests/                   # Unit tests
└── README.md
```

## CLI Usage

### adar (compiler)

```bash
adar build style.adar -o dist/
adar build src/ -o dist/ --minify
adar check file.adar
```

### adarpc (project manager)

```bash
adarpc init my-project    # Create new project
adarpc build              # Compile .adar to output/style/
adarpc serve              # Dev server at localhost:8080
adarpc watch              # Watch and rebuild on changes
```

## Development

```bash
pip install -e .
python -m pytest tests/ -v
adar check examples/src/button.adar
adar build examples/src/ -o examples/dist/
```

## License

MIT
