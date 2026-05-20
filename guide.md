# Adar Language Guide

> **Adar** is a modern, utility-first styling language with compile-time type checking. It compiles to modular, scoped CSS with native CSS nesting and CSS custom properties.

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Syntax Overview](#syntax-overview)
- [Variables](#variables)
- [CSS Rules](#css-rules)
- [Nesting](#nesting)
- [Mixins](#mixins)
- [Themes](#themes)
- [Functions](#functions)
- [Conditionals (`if`/`else`)](#conditionals-ifelse)
- [Imports](#imports)
- [Media Queries](#media-queries)
- [Type System](#type-system)
- [CSS Modules (Scoping)](#css-modules-scoping)
- [CLI Reference](#cli-reference)
- [Examples](#examples)
- [Editor Support](#editor-support)

---

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd adar

# Install
pip install -e .
```

**Requirements**: Python 3.11+

---

## Quick Start

Create a file `style.adar`:

```adar
// Variables
$primary = #3b82f6
$padding-md = 16px
$radius-md = 8px

// CSS Rule
.button {
    display: inline-flex
    padding: $padding-md $padding-md
    background: $primary
    color: white
    border-radius: $radius-md
    border: none
    cursor: pointer

    // Nesting with parent reference
    &:hover {
        background: #2563eb
    }

    // Media query inside rule
    @media (max-width: 768px) {
        width: 100%
    }
}
```

Compile it:

```bash
adar build style.adar -o dist/
```

Output (`dist/style.css`):

```css
.button__a1b2c3 {
    display: inline-flex;
    padding: 16px 16px;
    background: var(--primary);
    color: white;
    border-radius: var(--radius-md);
    border: none;
    cursor: pointer;
}
.button__a1b2c3:hover {
    background: #2563eb;
}
@media (max-width: 768px) {
    .button__a1b2c3 {
        width: 100%;
    }
}
```

Type-check without compiling:

```bash
adar check style.adar
```

---

## Syntax Overview

Adar syntax is CSS-like with some key differences:

- **Variables**: `$name = value` (compiles to CSS `var(--name)`)
- **Colons** separate property names from values: `property: value`
- **No semicolons required**: newlines separate declarations (semicolons optional)
- **Nesting**: rules can be nested inside other rules using `&` parent reference
- **Comments**: `//` for line comments, `/* */` for block comments
- **Space-separated values**: `margin: 10px 20px 10px 20px`
- **Keywords**: `theme`, `mixin`, `function`, `include`, `return`, `import`, `if`, `else`, `true`, `false`
- **Type checking**: 150+ CSS properties validated at compile time

---

## Variables

Variables are defined with `$` prefix and assigned with `=`:

```adar
// Colors
$primary = #3b82f6
$secondary = #10b981
$danger = #ef4444
$text-dark = #1e293b
$text-light = #94a3b8

// Spacing
$spacing-xs = 4px
$spacing-sm = 8px
$spacing-md = 16px
$spacing-lg = 24px
$spacing-xl = 32px

// Typography
$font-sans = "Inter", system-ui, sans-serif
$font-size-base = 16px
$font-size-lg = 20px
$line-height-base = 1.5

// Layout
$max-width = 1200px
$header-height = 64px
$sidebar-width = 280px

// Border radius
$radius-sm = 4px
$radius-md = 8px
$radius-lg = 16px

// Shadows
$shadow-sm = 0 1px 2px rgba(0, 0, 0, 0.05)
$shadow-md = 0 4px 6px rgba(0, 0, 0, 0.1)
```

Variables are referenced with `$name` and compile to CSS `var(--name)`:

```adar
.card {
    background: $primary        // -> background: var(--primary)
    padding: $spacing-md        // -> padding: var(--spacing-md)
    box-shadow: $shadow-sm      // -> box-shadow: var(--shadow-sm)
}
```

Variables defined at the top level are emitted into a `:root` block in CSS. Variables override within themes.

### Variable Types

Variables are type-checked at compile time:

```adar
$primary = #3b82f6     // type: COLOR
$size = 16px           // type: LENGTH
$ratio = 0.5           // type: NUMBER
$family = "Inter"      // type: STRING
```

---

## CSS Rules

Rules use standard CSS selectors:

```adar
// Class selector
.card {
    background: white
    border-radius: 8px
}

// Element selector
h1 {
    font-size: 32px
    font-weight: 700
}

// ID selector
#header {
    position: sticky
    top: 0
}

// Multiple selectors
h1, h2, h3 {
    line-height: 1.3
}

// Attribute selector
[data-active] {
    color: $primary
}

// Pseudo-classes
.btn {
    &:focus {
        outline: 2px solid $primary
    }
}
```

### Properties

Property-value pairs follow the format `property: value`. Values can include:

- Keywords: `red`, `flex`, `block`, `auto`
- Dimensions: `16px`, `2rem`, `50%`, `100vh`
- Numbers: `0`, `1.5`, `700`
- Hex colors: `#ff0000`, `#3b82f6`
- Strings: `"Inter"`, `"Helvetica Neue"`
- Variable references: `$primary`
- Space-separated lists: `10px 20px`
- Function calls: `rgba(0, 0, 0, 0.5)`
- Arithmetic: `100% - 20px`

```adar
.shadow-card {
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1)
}
```

---

## Nesting

Rules can be nested inside other rules, mirroring the CSS Nesting specification:

```adar
.card {
    padding: 16px
    background: white
    border-radius: 8px

    // Descendant selector
    .title {
        font-size: 20px
        font-weight: 700
    }

    .content {
        font-size: 14px
        color: #64748b
    }
}
```

Compiles to:

```css
.card__hash { padding: 16px; background: white; border-radius: 8px; }
.card__hash .title__hash { font-size: 20px; font-weight: 700; }
.card__hash .content__hash { font-size: 14px; color: #64748b; }
```

### Parent Reference `&`

Use `&` to reference the parent selector:

```adar
.btn {
    background: $primary
    color: white

    // & replaces with parent selector
    &:hover {
        background: #2563eb
    }

    &--large {
        padding: 16px 32px
        font-size: 18px
    }

    .icon & {
        padding: 4px
    }
}
```

Compiles to:

```css
.btn__hash { background: var(--primary); color: white; }
.btn__hash:hover { background: #2563eb; }
.btn__hash--large { padding: 16px 32px; font-size: 18px; }
.icon .btn__hash { padding: 4px; }
```

---

## Mixins

Mixins define reusable style blocks:

```adar
// Define a mixin
mixin card-base {
    background: white
    border-radius: 8px
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1)
}

// Use a mixin
.product-card {
    include card-base
    padding: 24px

    .title {
        font-size: 18px
        font-weight: 600
    }
}
```

### Mixins with Parameters

Mixins can accept parameters that compile to CSS custom properties:

```adar
mixin button-variant($bg, $color) {
    background: $bg
    color: $color
}

.btn-primary {
    include button-variant
    font-size: 16px
}
```

Parameters become `var(--name)` in the compiled CSS, allowing them to be overridden by the cascade.

---

## Themes

Themes let you define style variations. They compile to `[data-theme="name"]` CSS attribute selectors:

```adar
// Variables used by themes
$bg-primary = #ffffff
$text-primary = #1e293b
$accent = #3b82f6

// Default theme (wrapped in :root)
theme light {
    $bg-primary = #ffffff
    $text-primary = #1e293b
}

// Dark theme
theme dark {
    $bg-primary = #0f172a
    $text-primary = #f1f5f9
    $accent = #60a5fa
}

// Usage in components
.card {
    background: $bg-primary
    color: $text-primary
    border: 1px solid $accent
}
```

Compiles to:

```css
:root {
    --bg-primary: #ffffff;
    --text-primary: #1e293b;
    --accent: #3b82f6;
}
[data-theme="light"] {
    --bg-primary: #ffffff;
    --text-primary: #1e293b;
}
[data-theme="dark"] {
    --bg-primary: #0f172a;
    --text-primary: #f1f5f9;
    --accent: #60a5fa;
}
.card__hash {
    background: var(--bg-primary);
    color: var(--text-primary);
    border: 1px solid var(--accent);
}
```

Switch themes in HTML:

```html
<div data-theme="dark">
    <div class="card">...</div>
</div>
```

---

## Functions

### Predefined CSS Functions

Standard CSS functions pass through as-is to the output:

```adar
.button {
    background: rgba(59, 130, 246, 0.5)
    color: rgb(255, 255, 255)
    width: calc(100% - 40px)
    transform: rotate(45deg)
    transition: all 0.3s ease-in-out
}
```

### Custom Functions

Custom functions can be defined and are evaluated at compile time:

```adar
// Define a function
function spacing($n) {
    return $n * 4px
}

function rem($px) {
    return $px / 16px * 1rem
}

// Usage
.container {
    padding: spacing(4)     // compiles to: padding: calc(4 * 4px)
    font-size: rem(16)      // compiles to: font-size: calc(calc(16 / 16) * 1rem)
}
```

---

## Conditionals (`if`/`else`)

Compile-time branching with `if`/`else`:

```adar
$enable-shadows = true
$enable-rounded = false

.card {
    background: white
    padding: 16px

    if $enable-shadows {
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1)
    }

    if $enable-rounded {
        border-radius: 8px
    } else {
        border-radius: 0
    }
}
```

### Condition Expressions

```adar
$breakpoint = md
$button-style = "filled"

mixin responsive-padding($level) {
    padding: $level * 8px

    if $level > 3 {
        @media (max-width: 768px) {
            padding: $level * 4px
        }
    }
}

.nav {
    if $breakpoint == sm {
        flex-direction: column
    } else if $breakpoint == md {
        flex-direction: row
    } else {
        flex-direction: row
        gap: 24px
    }
}
```

Supported operators for conditions:

| Operator | Meaning     |
|----------|-------------|
| `==`     | Equal to    |
| `!=`     | Not equal   |
| `<`      | Less than   |
| `>`      | Greater than |
| `<=`     | Less or equal |
| `>=`     | Greater or equal |
| `and`    | Logical AND |
| `or`     | Logical OR  |
| `not`    | Logical NOT |

---

## Imports

Split your styles across multiple files:

```adar
// _variables.adar
import "variables"
import "mixins"
import "components/button"
import "components/card"
```

Imported files are included inline during compilation.

---

## Media Queries

Use `@media` for responsive styles:

```adar
// At top level
@media (max-width: 768px) {
    .container {
        padding: 16px
    }
}

// Nested inside rules
.sidebar {
    width: 280px

    @media (max-width: 768px) {
        width: 100%
        display: none

        &.open {
            display: block
        }
    }
}
```

---

## Type System

Adar validates CSS property values at compile time, catching errors before they reach the browser.

### Value Types

| Type       | Examples                           |
|------------|------------------------------------|
| `COLOR`    | `red`, `#ff0000`, `rgb(255,0,0)`  |
| `LENGTH`   | `16px`, `2rem`, `100vh`, `50%`     |
| `NUMBER`   | `0`, `1.5`, `700`                  |
| `ANGLE`    | `45deg`, `0.5turn`                 |
| `TIME`     | `0.3s`, `200ms`                    |
| `STRING`   | `"Inter"`, `"Helvetica"`           |
| `IDENT`    | any identifier keyword              |
| `ANY`      | any value                          |

### Type Checking Examples

```adar
// ✓ Valid — COLOR accepts keyword
.color-good { color: red }

// ✓ Valid — COLOR accepts hex
.color-good { color: #ff0000 }

// ✗ Type mismatch — LENGTH not allowed for COLOR
.color-bad { color: 16px }

// ✓ Valid — LENGTH accepts px, rem, %, vh, etc.
.width-good { width: 100px }
.width-good { width: 50% }
.width-good { width: 100vw }

// ✗ Type mismatch — COLOR not allowed for WIDTH
.width-bad { width: #ff0000 }

// ✓ Valid — custom properties accept any value
:root { --custom-value: 42px }
```

### Supported Properties

Adar type-checks 150+ CSS properties across these categories:

- **Layout**: `display`, `position`, `float`, `clear`, `overflow`, `visibility`
- **Box Model**: `width`, `height`, `margin`, `padding`, `box-sizing`, `min-width`/`max-width`/`min-height`/`max-height`
- **Border**: `border`, `border-width`, `border-style`, `border-color`, `border-radius`, individual sides
- **Background**: `background`, `background-color`, `background-image`, `background-size`, `background-position`, etc.
- **Typography**: `font`, `font-family`, `font-size`, `font-weight`, `line-height`, `text-align`, `text-decoration`
- **Flexbox**: `flex`, `flex-direction`, `flex-wrap`, `justify-content`, `align-items`, `gap`
- **Grid**: `grid`, `grid-template`, `grid-column`, `grid-row`, `gap`
- **Animation**: `transition`, `animation`, `transform`
- **Other**: `cursor`, `z-index`, `opacity`, `filter`, `box-shadow`, `outline`, `list-style`, `content`

Unknown properties generate warnings. Custom properties (`--*`) are always accepted.

---

## CSS Modules (Scoping)

By default, Adar scopes all class selectors with a content-based hash:

```css
/* Input: .btn { ... } */
/* Output: .btn__a1b2c3 { ... } */
```

A `.modules.json` mapping file is generated alongside the CSS:

```json
{
    "btn": "btn__a1b2c3",
    "card": "card__d4e5f6",
    "nav-header": "nav-header__g7h8i9"
}
```

Disable scoping with `--no-scope`:

```bash
adar build src/ -o dist/ --no-scope
```

---

## CLI Reference

### `adar build`

Compile `.adar` files to CSS.

```bash
# Single file
adar build style.adar -o dist/

# Directory (recursive)
adar build src/ -o dist/

# Type-check only (no output)
adar build style.adar --check

# Disable CSS Modules scoping
adar build src/ -o dist/ --no-scope

# Minified output
adar build src/ -o dist/ --minify
```

### `adar check`

Type-check without generating CSS.

```bash
# Single file
adar check style.adar

# Directory (recursive)
adar check src/
```

### Options

| Flag             | Description                              |
|------------------|------------------------------------------|
| `-o, --out DIR`  | Output directory (default: `dist/`)      |
| `--no-scope`     | Disable CSS Modules class scoping         |
| `--minify`       | Minify output (no whitespace)             |
| `--check`        | Type-check only, no CSS output            |
| `-h, --help`     | Show help message                         |

### `adarpc` (Project Manager)

Manage Adar projects with a robust, modular workflow. `adarpc` handles project initialization, dependency management, and build pipelines.

```bash
# Create a new modular project
adarpc init my-project

# Install dependencies from adarpc.toml
adarpc install

# Type-check all files in the project
adarpc check

# Build project (compile Adar and copy assets)
adarpc build

# Dev server with live reload
adarpc serve

# Watch and rebuild on changes
adarpc watch
```

#### Project Structure (Modular)

When you run `adarpc init`, a modular project structure is created:

```
my-project/
├── src/
│   ├── components/        # Reusable Adar components (mixins)
│   │   └── button.adar
│   ├── assets/            # Images, fonts, and other assets
│   ├── index.html         # HTML entry point
│   └── style.adar         # Main entry point (imports components)
├── output/                # Generated build (ready for deployment)
│   ├── style/
│   │   └── style.css      # Compiled & bundled CSS
│   ├── index.html         # Copied HTML
│   └── assets/            # Copied assets
├── adarpc.toml            # Project configuration
└── .gitignore
```

#### `adarpc build` Behavior

The `adarpc build` command performs the following actions:
1.  **Cleans/Prepares** the `output/` directory.
2.  **Compiles** all `.adar` files in `src/` to `output/style/`.
3.  **Resolves** all `import` statements, inlining library and component code.
4.  **Copies** all non-Adar files (HTML, PNG, SVG, etc.) from `src/` to `output/` maintaining the directory structure.

#### `adarpc.toml` Configuration

```toml
[project]
name = "my-project"
version = "0.1.0"
description = "A modular Adar project"

[build]
source = "src"            # Source directory
output = "output"         # Build output directory
minify = false            # Minify CSS output
scope = true              # Enable CSS Modules scoping

[dev]
port = 8080               # Dev server port
watch = true              # Enable watching in 'serve'
livereload = true         # Enable live reload in 'serve'

[dependencies]
tailwind-adar = "0.1.0"   # Library dependency
```

---

## Modular Project Architecture

For large-scale projects, follow these best practices for organizing your Adar code:

### 1. Component-Based Design
Break your UI into small, reusable components. Each component should be in its own `.adar` file under `src/components/` and expose its styles via **Mixins**.

```adar
// src/components/card.adar
mixin card-style($bg) {
    background: $bg
    padding: 20px
    border-radius: 8px
}
```

### 2. Centralized Variables
Keep your design tokens (colors, spacing, typography) in a dedicated file.

```adar
// src/theme.adar
$primary = #3b82f6
$spacing-unit = 4px
```

### 3. Entry Point Management
Use a single entry point (e.g., `style.adar`) to import everything. This ensures a single CSS bundle and consistent variable resolution.

```adar
// src/style.adar
import "theme"
import "components/card"
import "components/button"

.main-content {
    include card-style(white)
}
```

### 4. Asset Organization
Store images and fonts in `src/assets/`. `adarpc build` will automatically copy them to the output directory, making relative paths in your CSS work correctly.

---

## Best Practices for Modularity

- **Use Mixins for Components**: Instead of defining classes directly in component files, use mixins. This gives the consumer control over which class name to apply the styles to.
- **Prefix Library Variables**: When creating a library, prefix your variables (e.g., `$my-lib-primary`) to avoid collisions with user variables.
- **Explicit Imports**: Always import the specific files you need. Adar's compiler optimizes imports to prevent duplicate code.
- **Type Safety First**: Use `adarpc check` frequently during development to catch property errors before they break your layout.
- **Theme Scoping**: Use `theme` blocks for dark mode or multi-brand support instead of manual class toggling.

---

## Examples

### Button Component

```adar
// Button variants with mixin
$primary = #3b82f6
$danger = #ef4444
$radius = 6px

mixin btn-base {
    display: inline-flex
    align-items: center
    justify-content: center
    padding: 10px 20px
    font-size: 14px
    font-weight: 500
    border-radius: $radius
    border: none
    cursor: pointer
    transition: all 0.2s ease
}

.btn-primary {
    include btn-base
    background: $primary
    color: white

    &:hover {
        background: #2563eb
    }
}

.btn-danger {
    include btn-base
    background: $danger
    color: white

    &:hover {
        background: #dc2626
    }
}

.btn-large {
    include btn-base
    padding: 14px 28px
    font-size: 16px
}
```

### Card with Dark Mode

```adar
// Theme-aware card component
$bg-card = #ffffff
$text-card = #1e293b
$border-card = #e2e8f0

theme light {
    $bg-card = #ffffff
    $text-card = #1e293b
    $border-card = #e2e8f0
}

theme dark {
    $bg-card = #1e293b
    $text-card = #f1f5f9
    $border-card = #334155
}

.card {
    background: $bg-card
    color: $text-card
    border: 1px solid $border-card
    border-radius: 12px
    padding: 24px

    .title {
        font-size: 20px
        font-weight: 600
        margin-bottom: 8px
    }

    .description {
        font-size: 14px
        line-height: 1.6
        opacity: 0.8
    }

    &:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1)
    }
}
```

### Responsive Grid

```adar
$enable-animations = true

.grid {
    display: grid
    grid-template-columns: repeat(3, 1fr)
    gap: 24px

    @media (max-width: 1024px) {
        grid-template-columns: repeat(2, 1fr)
    }

    @media (max-width: 640px) {
        grid-template-columns: 1fr
    }

    .item {
        background: white
        padding: 24px
        border-radius: 8px

        if $enable-animations {
            transition: all 0.3s ease

            &:hover {
                transform: translateY(-4px)
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12)
            }
        }
    }
}
```

---

## Error Messages & Debugging

Adar errors include the file name, line number, and column where the error occurred.

### Error Format

```
Error [test.adar:5:12]: Type mismatch for 'color': expected [COLOR, IDENT], got LENGTH
```

### Common Errors

| Error | Cause | Example |
|-------|-------|---------|
| `Type mismatch` | Wrong value type for property | `color: 16px` |
| `Unknown CSS property` | Property not in CSS spec | `unknown-prop: x` |
| `Undefined variable` | Variable not declared | `$undefined` |
| `Undefined mixin` | Mixin not defined before use | `include missing` |
| `Binary operation type mismatch` | Incompatible types in expression | `10px + red` |
| `Unexpected statement` | Syntax error or misplaced statement | `return` outside function |
| `Function expects N arguments, got M` | Wrong argument count | `spacing(1, 2, 3)` |

### Debugging Tips

1. **Use `adar check`**: Run type-checking without generating CSS to find all errors
2. **Check variable names**: Variables are case-sensitive (`$Primary` vs `$primary`)
3. **Verify mixin order**: Mixins must be defined before they are included
4. **Check selector syntax**: Complex selectors may need simplification
5. **Use `--no-scope`**: Disable scoping temporarily to isolate hash-related issues

---

## Variable Scoping Rules

Adar variables follow a cascading scope model:

### Global Scope

Variables declared at the top level are available everywhere:

```adar
// Global variable — available in all rules and mixins
$primary = #3b82f6
$radius = 8px
```

### Theme Scope

Variables inside a `theme` block override global values within that theme:

```adar
theme dark {
    $primary = #60a5fa   // overrides --primary inside [data-theme="dark"]
}
```

### Block Scope

Variables declared inside a rule block are available within that block only:

```adar
.card {
    $local-padding = 16px   // only available inside this rule
    padding: $local-padding
}
```

### Resolution Order

When a variable is referenced, Adar resolves it in this order:
1. Current block scope (innermost)
2. Theme scope (if inside a theme block)
3. Global scope (top-level)

### Important Note

Adar variables compile to CSS custom properties (`var(--name)`), not preprocessor-style text substitution. This means:
- Variables are dynamically resolved at runtime by the browser
- Theme overrides work via the CSS cascade
- Variables cannot be used in selectors or at-rule parameters

---

## @keyframes & Animations

Adar supports CSS animations through standard property validation:

```adar
// Define keyframes in CSS and reference by name
@keyframes fadeIn {
    from { opacity: 0 }
    to { opacity: 1 }
}

// Use animation properties
.element {
    animation-name: fadeIn
    animation-duration: 0.3s
    animation-timing-function: ease-in-out
    animation-delay: 0.1s
    animation-iteration-count: 1
    animation-fill-mode: both
}

// Shorthand
.element {
    animation: fadeIn 0.3s ease-in-out
}
```

> **Note**: `@keyframes` blocks pass through verbatim to the CSS output. The type checker validates animation-related properties.

---

## Build Pipeline

Understanding the compilation pipeline helps with debugging:

```
Source (.adar file)
      |
      v
  ┌──────────┐
  │  LEXER   │  Tokenizes source code into tokens
  │          │  Handles: numbers, strings, identifiers, comments
  └────┬─────┘
       | tokens
       v
  ┌──────────┐
  │  PARSER  │  Builds AST from tokens
  │          │  Handles: rules, variables, mixins, functions
  └────┬─────┘
       | AST (Stylesheet)
       v
  ┌──────────┐
  │ CHECKER  │  Validates property types against CSS spec
  │          │  Checks: variable types, mixin references, binary ops
  └────┬─────┘
       | checked AST
       v
  ┌──────────┐
  │ RESOLVER │  Expands mixins, manages variable scopes
  │          │  Handles: mixin includes, scope tracking
  └────┬─────┘
       | resolved AST
       v
  ┌──────────┐
  │CODEGEN   │  Generates CSS output
  │          │  Handles: scoping, minification, conditionals
  └────┬─────┘
       | CSS string
       v
   Output (.css + .modules.json)
```

Each stage can produce errors that halt the pipeline. The `adar check` command runs through the checker stage, while `adar build` runs the full pipeline.

---

## Using Adar as a Python Library

Adar's compiler modules can be imported and used programmatically:

```python
from adar.lexer import Lexer
from adar.parser import Parser
from adar.checker import Checker
from adar.resolver import Resolver
from adar.codegen import CodeGenerator

# Full compilation pipeline
def compile_adar(source: str, filename: str = "style.adar") -> str:
    # 1. Lex
    lexer = Lexer(source, filename=filename)
    tokens = lexer.tokenize()

    # 2. Parse
    parser = Parser(tokens)
    ast = parser.parse()

    # 3. Type check
    checker = Checker()
    result = checker.check(ast)
    if not result.ok:
        for err in result.errors:
            print(f"Error: {err.message}")
        return ""

    # 4. Resolve mixins & variables
    resolver = Resolver()
    resolved = resolver.resolve(ast)

    # 5. Generate CSS
    gen = CodeGenerator()
    return gen.generate(resolved)
```

### API Reference

| Class | Module | Description |
|-------|--------|-------------|
| `Lexer(source, filename)` | `adar.lexer` | Tokenizes source text |
| `Parser(tokens)` | `adar.parser` | Builds AST from tokens |
| `Checker(spec?)` | `adar.checker` | Validates property types |
| `CSSSpec()` | `adar.checker` | CSS property definitions |
| `Resolver()` | `adar.resolver` | Resolves mixins & variables |
| `CodeGenerator(scoped?, pretty?)` | `adar.codegen` | Generates CSS output |

---

## Library Ecosystem (adarlib)

Adar has a growing ecosystem of component and utility libraries available through `adarpc` — the Adar package manager.

### Available Libraries

| Library | Version | Description |
|---------|---------|-------------|
| **tailwind-adar** | 0.1.0 | Tailwind CSS utility classes — spacing, colors, typography, layout, shadows, responsive |
| **daisy-adar** | 0.1.0 | Component library inspired by daisyUI — buttons, cards, badges, alerts, themes |
| **material-adar** | 0.1.0 | Material Design 3 components — buttons, cards, chips, dialogs, typography system |

All libraries are open-source and hosted on GitHub:
[https://github.com/zulsyam23-dot/adarlib](https://github.com/zulsyam23-dot/adarlib)

### Installing Libraries

```bash
# Install a library
adarpc install tailwind-adar

# Install multiple libraries
adarpc install daisy-adar material-adar

# Install all libraries listed in adarpc.toml
adarpc install
```

Installed libraries are placed in `adar_modules/` directory in your project.

### Using Libraries

After installing a library, import it in your `.adar` file:

```adar
// Import the entire library
import "tailwind-adar"

// Or import specific files from a library
import "daisy-adar/button"
```

Library imports are resolved at compile time — the library's styles are inlined
into the output CSS.

### Searching for Libraries

```bash
# Search the registry
adarpc search button
adarpc search material
adarpc search tailwind
```

### Listing Installed Libraries

```bash
adarpc list
```

### Managing Dependencies

Add libraries to your `adarpc.toml` to declare them as project dependencies:

```toml
[dependencies]
tailwind-adar = "0.1.0"
daisy-adar = "0.1.0"
material-adar = "0.1.0"
```

Then install all dependencies at once:

```bash
adarpc install
```

This downloads and installs all declared libraries into `adar_modules/`.

### Creating a Library

To create your own Adar library:

1. Create a directory with an `adarpc.toml` metadata file:
   ```toml
   [package]
   name = "my-library"
   version = "0.1.0"
   description = "My component library"
   ```

2. Create `index.adar` with your components and utilities.

3. Submit your library to the community at:
   [https://github.com/zulsyam23-dot/adarlib](https://github.com/zulsyam23-dot/adarlib)

### Library Structure

A well-structured Adar library follows these conventions:

```
my-library/
├── adarpc.toml      # Package metadata (name, version, description)
├── index.adar       # Main entry point (imported by default)
├── button.adar      # Individual components (optional)
├── card.adar
└── utilities.adar
```

Users can import specific files:
```adar
import "my-library"            # imports index.adar
import "my-library/button"     # imports button.adar
```

---

## File Extension

Use `.adar` for Adar source files.

---

## Why Adar?

| Feature                | Adar | Pure CSS | Sass/SCSS | Tailwind |
|------------------------|------|----------|-----------|----------|
| Type checking          | ✓    | ✗        | ✗         | ✓ (JIT)  |
| CSS Modules            | ✓    | ✗        | ✗         | ✗        |
| Themes                 | ✓    | ✓ (var)  | ✓         | ✓        |
| Mixins                 | ✓    | ✗        | ✓         | ✗        |
| Functions              | ✓    | ✗        | ✓         | ✗        |
| Nesting                | ✓    | ✓ (spec) | ✓         | ✗        |
| Compile-time if/else   | ✓    | ✗        | ✗         | ✗        |
| CSS variables output   | ✓    | ✗        | ✗         | ✗        |
| Property validation    | ✓    | ✗        | ✗         | ✗        |
| No runtime             | ✓    | ✓        | ✓         | ✓        |

---

*Adar v0.1.0 — CSS-like styling language with compile-time type checking.*
