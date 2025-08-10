# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DesignSpace Sketch (DSSketch) is a Python tool that provides bidirectional conversion between compact `.dssketch` format and verbose `.designspace` XML files. It achieves 84-97% size reduction while maintaining full functionality for variable font design.

## Key Commands

### Running the converter
```bash
# Primary CLI (preferred method) - UFO validation and optimization by default
python dssketch_cli.py font.designspace
python dssketch_cli.py font.dssketch

# Backwards compatibility
python dssketch.py font.designspace  # still works

# With output file
python dssketch_cli.py input.designspace -o output.dssketch

# Skip UFO validation (not recommended)
python dssketch_cli.py font.dssketch --no-validation

# Allow missing UFO files
python dssketch_cli.py font.dssketch --allow-missing-ufos
```

### Development setup
```bash
# Install dependencies
pip install -r requirements.txt

# Dependencies: fonttools, fontParts, designspaceProblems, icecream
```

### Testing examples
```bash
# Test with provided examples
python dssketch_cli.py examples/KazimirText-Variable.designspace
python dssketch_cli.py examples/Onweer_v2_RAIN.dssketch
python dssketch_cli.py examples/wildcard-test.dss
```

## Architecture & Core Concepts

### Main Components

**Module Structure:**
- `dssketch.py` - Core library with conversion classes
- `dssketch_cli.py` - Command-line interface (preferred for CLI usage)

**Core Classes:**
- `DSSParser` - Parses .dssketch format into structured data
- `DSSWriter` - Generates .dssketch from structured data  
- `DesignSpaceToDSS` - Converts .designspace → DSSketch
- `DSSToDesignSpace` - Converts DSSketch → .designspace (supports discrete axes)
- `UFOValidator` - Validates UFO master files existence and structure
- `Standards` - Built-in weight/width mappings (100=Thin, 400=Regular, etc.)

### Critical Design Concepts

**User Space vs Design Space:**
- User Space: Values users see (font-weight: 400)
- Design Space: Actual coordinates in font files (can be any value)
- Mapping: `Regular > 362` means user requests 400, master is at 362

**Axis Types:**
- Standard axes use lowercase tags: `wght`, `wdth`, `ital`, `slnt`, `opsz`
- Custom axes use uppercase: `CONTRAST CNTR`
- Discrete axes: `ital discrete` or `ital 0:0:1` for non-interpolating axes (like italic on/off)

**Discrete Axes:**
- Used for axes that don't interpolate (e.g., Roman vs Italic)
- Format: `ital discrete` (preferred) or `ital 0:0:1` (verbose)
- Simplified labels: just `Upright` and `Italic` (no redundant > values)
- Supports multiple label names: Upright/Roman/Normal for 0, Italic for 1
- Labels stored in `data/discrete-axis-labels.yaml` for easy customization
- Both old and new formats supported for backward compatibility
- Generates DesignSpace `values="0 1"` attribute instead of `minimum/maximum`
- Essential for proper variable font generation with non-compatible masters

### DSSketch Format Structure

```dssketch
family FontName
suffix VF  # optional
path masters  # common directory for masters

axes
    wght 100:400:900  # min:default:max
        Thin > 100    # label > design_value
        Regular > 400
    ital discrete  # discrete axis (equivalent to ital 0:0:1)
        Upright    # simplified format (no > 0.0 needed)
        Italic     # simplified format (no > 1.0 needed)

masters
    # If path is set, just filename needed:
    MasterName [362, 0] @base  # [coordinates] @flags
    
    # Or individual paths per master:
    # upright/Light [100]
    # italic/Bold [900]
    
rules
    dollar > dollar.rvrn (weight >= 480) "dollar alternates"
    cent* > .rvrn (weight >= 480) "cent patterns"  # wildcard patterns

instances auto  # or explicit list
```

### Key Features

**Wildcard Patterns:**
- Pattern detection in rules (line ~1100)
- Supports `*` wildcards: `dollar* cent*`
- Target patterns: `.rvrn` suffix

**Rule Conditions:**
- Simple: `(weight >= 480)`
- Compound: `(weight >= 600 && width >= 110)`
- Exact: `(weight == 500)`
- Range: `(80 <= width <= 120)`

**Optimization:**
- Auto-compresses multiple similar rules into wildcard patterns
- Detects standard weight/width values
- Removes redundant mappings

**Path Management:**
- Auto-detects common master directories (e.g., "masters/")
- Supports mixed paths for masters in different directories
- `path` parameter in DSSketch format for common directory

**UFO Validation (enabled by default):**
- Automatically checks UFO file existence and structure
- Fails conversion on missing files by default
- `--no-validation` skips validation (not recommended)
- `--allow-missing-ufos` continues even with missing files
- Validates metainfo.plist, fontinfo.plist, and glyphs directory

## Important Implementation Details

### Current Limitations (from NEXT_STEPS.md)

1. **Hardcoded glyph names** (line ~1104): Wildcard expansion uses fixed list instead of reading from UFO files
2. **No UFO validation**: Missing files aren't detected during conversion
3. **Limited pattern detection**: Only supports prefix/suffix wildcards

### Data Files

- `data/stylenames.json` - Standard weight/width mappings
- `data/unified-mappings.yaml` - Extended axis mappings
- `data/font-resources-translations.json` - Localization data
- `data/discrete-axis-labels.yaml` - Standard labels for discrete axes (ital, slnt)

### File Extensions

- `.dssketch` or `.dss` - DSSketch format (compact)
- `.designspace` - DesignSpace XML (verbose)
- Both directions preserve full functionality

## Performance Characteristics

Typical compression ratios:
- 2D fonts (weight×italic): 84-85% size reduction
- 4D fonts (weight×width×contrast×slant): 97% size reduction
- Complex fonts: Up to 36x smaller (Onweer: 204KB → 5.6KB)

## Common Development Tasks

When modifying the converter:
1. Test with all examples in `examples/` directory
2. Ensure bidirectional conversion preserves data
3. Check wildcard pattern detection/expansion
4. Validate axis mapping integrity

When adding features:
1. Update both parser and writer components
2. Test with `--optimize` and `--no-optimize` flags
3. Verify complex rules with compound conditions
4. Check handling of both standard and custom axes