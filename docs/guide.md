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

- **Variables**: `$name = value`
- **No semicolons required**: newlines separate declarations (semicolons optional)
- **Nesting**: rules can be nested inside other rules
- **Parent reference**: `&` references the parent selector
- **Comments**: `//` for line comments
- **Space-separated values**: `margin: 10px 20px 10px 20px`
- **Keywords**: `theme`, `mixin`, `function`, `include`, `return`, `import`, `if`, `else`, `true`, `false`

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

### Custom Functions (Experimental)

Custom functions can be defined but currently pass through without evaluation:

```adar
// Define a function
function spacing($n) {
    return $n * 4px
}

function rem($px) {
    return $px / 16px * 1rem
}

// Usage (output compiles to literal function call)
.container {
    padding: spacing(4)
    font-size: rem(16)
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

Manage Adar projects with a Cargo-like workflow.

```bash
# Create a new project
adarpc init my-project

# Build (compile .adar to output/style/)
adarpc build

# Dev server with live reload
adarpc serve

# Watch and rebuild on changes
adarpc watch
```

Project structure created by `adarpc init`:

```
my-project/
├── src/
│   ├── index.html         # HTML source
│   └── style.adar         # Adar source
├── output/
│   └── style/
│       └── style.css      # Compiled CSS
├── adarpc.toml            # Project config
└── .gitignore
```

### `adarpc.toml`

```toml
[project]
name = "my-project"
version = "0.1.0"

[build]
output = "output"
minify = false
scope = false
source = "src"

[dev]
port = 8080
watch = true
livereload = true
```

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
