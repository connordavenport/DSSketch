# DSSketch Data Customization Guide

**Complete guide to customizing DSSketch data files for advanced font development workflows**

## 📖 Overview

DSSketch uses a flexible data file system that allows you to customize axis mappings, discrete axis labels, and other configuration settings. This enables:

- **Custom weight/width values** - Add your own label names (e.g., "UltraBlack", "Hairline")
- **Discrete axis customization** - Define custom labels for italic, slant, and other discrete axes
- **Team standards** - Share common mappings across projects via version control
- **Legacy compatibility** - Override defaults without modifying package code

The data system powers DSSketch's **label-based syntax**, allowing you to write:
```dssketch
wght Thin:Regular:Black    # Instead of 100:400:900
sources [wght, ital]
    Font-Regular [Regular, Upright] @base    # Instead of [400, 0]
```

## 🏗️ Data Files Architecture

### Two-Level Priority System

DSSketch uses a cascading data file system:

1. **Package data** (read-only) - Default files shipped with DSSketch
   - Location: `<package>/src/dssketch/data/`
   - Updated when you upgrade DSSketch
   - Safe fallback values

2. **User data** (customizable) - Your modifications
   - Platform-specific locations (see below)
   - Takes priority over package defaults
   - Persists across DSSketch upgrades

### User Data Locations

The `DataManager` automatically determines the correct location:

| Platform | Default Location | Environment Override |
|----------|-----------------|---------------------|
| **macOS** | `~/Library/Application Support/dssketch/` | `DSSKETCH_DATA_DIR` |
| **Linux** | `~/.config/dssketch/` (or `$XDG_CONFIG_HOME/dssketch/`) | `DSSKETCH_DATA_DIR` |
| **Windows** | `%APPDATA%\dssketch\` | `DSSKETCH_DATA_DIR` |

### Loading Priority

When DSSketch needs data, it checks:

```
1. User file (if exists) → USE THIS
2. Package file          → USE THIS
3. Empty dictionary      → Fallback
```

User files **completely override** package files (no merging).

## 📂 Available Data Files

### `unified-mappings.yaml` ⭐ Primary Configuration

**Purpose**: Maps style names to numeric values for weight and width axes

> ⚠️ **Important**: Width axis uses **1-9 OS/2 scale** (not percentages!). Weight uses direct user-space values.

**Structure** (Compact Schema v2.0):
```yaml
weight:
  # Basic format: label name with user_space value
  Thin:
    user_space: 100

  Regular:
    user_space: 400

  Bold:
    user_space: 700

  # Alias format: inherits all values from another entry
  SemiBold:
    alias_of: Semibold

  # Italic variants: same user_space, but with style marker
  "Regular Italic":
    user_space: 400
    style: italic

width:
  # Width needs both os2 and user_space (they differ!)
  # OS/2 uses 1-9 scale, user_space uses design coordinates
  Condensed:
    os2: 3          # Condensed in OS/2 spec (1-9 scale)
    user_space: 80  # Design space coordinate

  Normal:
    os2: 5          # Medium/Normal in OS/2 spec
    user_space: 100

  Extended:
    os2: 8          # Extra-expanded in OS/2 spec
    user_space: 150
```

**Key Concepts**:
- **weight**: Only `user_space` needed (OS/2 value = user_space for weight)
- **width**: Both `os2` and `user_space` required (they differ significantly!)
  - `os2`: Uses **1-9 scale** per OpenType OS/2 specification
    - 1 = Ultra-condensed
    - 5 = Normal/Medium
    - 9 = Ultra-expanded
  - `user_space`: Design space coordinate (typically 60-200)
- **Aliases**: Use `alias_of` to avoid duplication
- **Style markers**: Add `style: italic` for italic variants

**Used by**:
- `Standards` class (`src/dssketch/core/mappings.py`)
- Label-based axis ranges: `wght Thin:Regular:Black`
- Label-based source coordinates: `[Regular, Upright]`
- Label-based rule conditions: `(weight >= Bold)`
- Validation and typo detection

### `discrete-axis-labels.yaml` ⭐ Discrete Axes

**Purpose**: Defines label names for discrete axes (non-interpolating)

**Structure**:
```yaml
ital:
  0:
    - "Upright"    # Primary name
    - "Roman"      # Alias
    - "Normal"     # Alias
  1:
    - "Italic"

slnt:
  0:
    - "Upright"
    - "Normal"
  1:
    - "Slanted"
    - "Oblique"

```

**Key Concepts**:
- **Multiple aliases**: First name is primary, others are recognized alternatives
- **Numeric keys**: Map to actual axis values (0, 1, etc.)
- **Order matters**: First name used for output, all names recognized for input

**Used by**:
- `DiscreteAxisHandler` class (`src/dssketch/utils/discrete.py`)
- Simplified discrete axis syntax: `Upright` instead of `Upright > 0.0`
- Parser validation and normalization

### `font-resources-translations.json`

**Purpose**: Localization data for font metadata

**Structure**:
```json
{
  "Regular": {
    "en": "Regular",
    "de": "Normal",
    "fr": "Régulier"
  }
}
```

**Used by**:
- `DesignSpaceToDSS` converter for international font names

### `stylenames.json` ⚠️ DEPRECATED

**Status**: Kept for backward compatibility only

**Migration**: Use `unified-mappings.yaml` instead

**Note**: This file is no longer actively used by DSSketch. If you have customizations in `stylenames.json`, migrate them to `unified-mappings.yaml`.

## 🔧 How Data Files Are Used

### Label-Based Syntax (`Standards` Class)

The `Standards` class (`src/dssketch/core/mappings.py`) provides methods for resolving labels:

```python
from dssketch.core.mappings import Standards

# Get user-space value for a label
value = Standards.get_user_space_value("Bold", "weight")  # → 700.0

# Get label for a user-space value
name = Standards.get_name_by_user_space(400, "weight")    # → "Regular"

# Check if label exists
exists = Standards.has_mapping("ExtraBlack", "weight")    # → True/False
```

**This enables**:
```dssketch
# Axis ranges with labels
wght Thin:Regular:Black

# Source coordinates with labels
sources [wght, ital]
    Font-Regular [Regular, Upright] @base

# Rule conditions with labels
rules
    dollar > dollar.heavy (weight >= Bold)
```

### Discrete Axes (`DiscreteAxisHandler`)

The `DiscreteAxisHandler` class (`src/dssketch/utils/discrete.py`) manages discrete axis labels:

```python
from dssketch.utils.discrete import DiscreteAxisHandler

handler = DiscreteAxisHandler()

# Load labels from data file
labels = handler.load_discrete_labels()

# Get labels for specific axis
ital_labels = handler.get_labels("ital")
# → {0: ["Upright", "Roman", "Normal"], 1: ["Italic"]}
```

**This enables**:
```dssketch
# Simplified discrete axis format
ital discrete
    Upright    # Instead of: Upright > 0.0
    Italic     # Instead of: Italic > 1.0
```

### Validation and Typo Detection

The `DSSValidator` uses mappings to detect typos:

```dssketch
# Detects typo in weight label
wght 100:900
    Lite > 300    # ⚠️ Warning: "Did you mean 'Light'?"
    Bol > 700     # ⚠️ Warning: "Did you mean 'Bold'?"
```

Uses **Levenshtein distance algorithm** (like git, npm, bash) with threshold of 2 characters.

## 🛠️ Managing Data Files

### CLI Commands

#### After `pip install -e .`:

```bash
# Show data file locations and status
dssketch-data info

# Copy package file to user directory for editing
dssketch-data copy unified-mappings.yaml

# Open user data directory in file manager
dssketch-data edit

# Reset specific file to package default
dssketch-data reset --file unified-mappings.yaml

# Reset all user files to package defaults
dssketch-data reset --all

# Show user data directory path
dssketch-data path
```

#### Without installation:

```bash
python -m dssketch.data_cli info
python -m dssketch.data_cli copy unified-mappings.yaml
python -m dssketch.data_cli edit
python -m dssketch.data_cli reset --all
```

### Programmatic Access (Python API)

#### Using `DataManager`:

```python
from dssketch.config import get_data_manager

dm = get_data_manager()

# Get information about data files
info = dm.get_data_info()
print(f"User directory: {info['user_data_dir']}")
print(f"User files: {info['user_files']}")
print(f"Package files: {info['package_files']}")

# Load data file (user override priority)
mappings = dm.load_data_file("unified-mappings.yaml")

# Modify data
mappings['weight']['UltraBlack'] = {'user_space': 950}

# Save to user directory
dm.save_user_data("unified-mappings.yaml", mappings)

# Copy package file to user directory
dm.copy_package_to_user("discrete-axis-labels.yaml")

# Reset to defaults
dm.reset_to_defaults("unified-mappings.yaml")  # Specific file
dm.reset_to_defaults()  # All files
```

#### Using convenience functions:

```python
from dssketch.config import (
    load_unified_mappings,
    load_discrete_labels,
    load_translations
)

# Load with automatic user override
mappings = load_unified_mappings()
discrete = load_discrete_labels()
translations = load_translations()
```

## 💡 Customization Examples

### Example 1: Add Custom Weight

**Goal**: Add "UltraBlack" (950) and "Hairline" (50) weights

1. Copy default file:
   ```bash
   dssketch-data copy unified-mappings.yaml
   ```

2. Edit `~/Library/Application Support/dssketch/unified-mappings.yaml`:
   ```yaml
   weight:
     # ... existing weights ...

     Hairline:
       user_space: 50

     UltraBlack:
       user_space: 950
   ```

3. Use in DSSketch:
   ```dssketch
   family MyFont

   axes
       wght Hairline:Regular:UltraBlack
           Hairline > 50
           Regular > 400
           UltraBlack > 950

   sources [wght]
       Font-Hairline [Hairline]
       Font-Regular [Regular] @base
       Font-UltraBlack [UltraBlack]
   ```

### Example 2: Add Custom Width Values

**Goal**: Add custom "SuperCompressed" and "SuperWide" widths beyond standard range

```yaml
width:
  # ... existing widths ...

  # Note: os2 uses 1-9 scale per OS/2 specification
  # Standard range: 1 (Ultra-condensed) to 9 (Ultra-expanded)

  SuperCompressed:
    os2: 1          # Use Ultra-condensed (1) - minimum OS/2 value
    user_space: 50  # Custom design space coordinate

  SuperWide:
    os2: 9          # Use Ultra-expanded (9) - maximum OS/2 value
    user_space: 250 # Custom design space coordinate
```

### Example 3: Customize Discrete Axis Labels

**Goal**: Add "Cursive" as alias for Italic

```yaml
ital:
  0:
    - "Upright"
    - "Roman"
  1:
    - "Italic"
    - "Cursive"    # New alias
    - "Oblique"    # New alias
```

**Now you can write**:
```dssketch
ital discrete
    Roman       # Recognized as 0
    Cursive     # Recognized as 1
```

### Example 4: Add Custom Discrete Axis

**Goal**: Add MOOD axis with Serious/Playful values

1. Edit `discrete-axis-labels.yaml`:
   ```yaml
   MOOD:
     0:
       - "Serious"
       - "Professional"
     1:
       - "Playful"
       - "Fun"
   ```

2. Use in DSSketch:
   ```dssketch
   axes
       MOOD discrete
           Serious
           Playful
   ```

### Example 5: Create Aliases

**Goal**: Add "Demi" as alias for "Semibold"

```yaml
weight:
  Semibold:
    user_space: 600

  Demi:
    alias_of: Semibold

  DemiBold:
    alias_of: Semibold
```

All three names now resolve to the same value (600).

### Example 6: Team-Wide Custom Standards

**Goal**: Share custom mappings across a team

1. Create custom mappings in your project:
   ```
   my-font-project/
   ├── .dssketch/
   │   └── unified-mappings.yaml
   ├── sources/
   └── MyFont.dssketch
   ```

2. Set environment variable in project:
   ```bash
   export DSSKETCH_DATA_DIR="$(pwd)/.dssketch"
   ```

3. Commit `.dssketch/` to git
4. Team members use same mappings automatically

## ⚙️ Best Practices

### File Format Guidelines

1. **Use YAML for readability** - `.yaml` preferred over `.json`
2. **Maintain consistent indentation** - Use 2 spaces (YAML standard)
3. **Quote special characters** - `"Regular Italic"`, not `Regular Italic`
4. **Use UTF-8 encoding** - Required for international characters
5. **Follow compact schema** - Use `alias_of` instead of duplicating values

### Validation Tips

1. **Check YAML syntax** before saving:
   ```bash
   python -c "import yaml; yaml.safe_load(open('unified-mappings.yaml'))"
   ```

2. **Verify after changes**:
   ```bash
   dssketch-data info    # Should show your file in "User files"
   ```

3. **Test with simple DSSketch file**:
   ```dssketch
   family Test
   axes
       wght YourCustomLabel:Regular:Black
   sources [wght]
       Test-Regular [Regular] @base
   instances auto
   ```

### Backup Recommendations

1. **Before major changes**:
   ```bash
   cp ~/Library/Application\ Support/dssketch/unified-mappings.yaml{,.backup}
   ```

2. **Version control user data**:
   ```bash
   git add .dssketch/
   git commit -m "Custom weight mappings for project"
   ```

3. **Reset if something breaks**:
   ```bash
   dssketch-data reset --all
   ```

### Debugging Data Issues

1. **Check which files are loaded**:
   ```bash
   dssketch-data info
   ```

2. **Verify user file is being used**:
   ```bash
   # Should show your file with "(overridden)" marker
   dssketch-data info
   ```

3. **Test without user data**:
   ```bash
   dssketch-data reset --all
   # Run your conversion
   # If it works, issue is in your user data
   ```

4. **Enable debug logging**:
   ```python
   from dssketch.utils.logging import DSSketchLogger
   DSSketchLogger.setup_logger("test.dssketch", "DEBUG")
   ```

## 🔬 Advanced Topics

### Environment Variables

**`DSSKETCH_DATA_DIR`** - Override default user data location

```bash
# Per-project data directory
export DSSKETCH_DATA_DIR="$(pwd)/.dssketch"

# Shared team directory
export DSSKETCH_DATA_DIR="/shared/team/dssketch-data"

# Temporary custom settings
DSSKETCH_DATA_DIR=/tmp/test-mappings dssketch font.designspace
```

**Use cases**:
- Project-specific mappings
- Team-wide standards
- Testing different configurations
- CI/CD pipelines

### Integration with Version Control

**Recommended structure**:
```
font-project/
├── .dssketch/                    # Commit this!
│   ├── unified-mappings.yaml     # Project standards
│   └── discrete-axis-labels.yaml
├── .gitignore
├── sources/
│   ├── Font-Regular.ufo
│   └── ...
├── MyFont.dssketch
└── README.md
```

**`.gitignore`**:
```gitignore
# Don't commit system-wide user data
~/Library/Application Support/dssketch/
~/.config/dssketch/

# DO commit project-specific data
!.dssketch/
```

**Setup script** (`setup.sh`):
```bash
#!/bin/bash
export DSSKETCH_DATA_DIR="$(pwd)/.dssketch"
echo "Using project data directory: $DSSKETCH_DATA_DIR"
```

### Team Workflows

**Scenario**: Design team with custom weight scale

1. **Define team standards** (`.dssketch/unified-mappings.yaml`):
   ```yaml
   weight:
     XLight: {user_space: 250}
     Light: {user_space: 350}
     Regular: {user_space: 450}
     Medium: {user_space: 550}
     Bold: {user_space: 650}
     XBold: {user_space: 750}
   ```

2. **Commit to repository**:
   ```bash
   git add .dssketch/
   git commit -m "Add team-wide weight standards"
   ```

3. **Team members use**:
   ```bash
   cd font-project
   export DSSKETCH_DATA_DIR="$(pwd)/.dssketch"
   dssketch MyFont.designspace  # Uses team mappings
   ```

4. **CI/CD integration**:
   ```yaml
   # .github/workflows/build.yml
   - name: Build font
     run: |
       export DSSKETCH_DATA_DIR="$(pwd)/.dssketch"
       dssketch sources/MyFont.designspace
   ```

## 🔍 Technical Details

### DataManager Implementation

**Singleton pattern** - One instance per process:
```python
# Get the singleton instance
dm = get_data_manager()
```

**File resolution algorithm**:
```python
def load_data_file(filename):
    user_file = user_data_dir / filename
    if user_file.exists():
        return load(user_file)     # User override

    package_file = package_data_dir / filename
    if package_file.exists():
        return load(package_file)  # Package default

    return {}                      # Empty fallback
```

**Automatic format detection**:
- `.yaml`/`.yml` → YAML parser
- `.json` → JSON parser
- No extension → Try YAML, fallback to JSON

### Update Behavior

When you upgrade DSSketch:

| File Type | Behavior |
|-----------|----------|
| **Package files** | Updated automatically with new DSSketch version |
| **User files** | Remain unchanged (your customizations preserved) |
| **New fields** | Package defaults used for missing fields |

**Example**:
```
Package v1.0:     User v1.0:       Package v1.1:     User (unchanged):
weight:           weight:          weight:           weight:
  Regular: 400      Bold: 750        Regular: 400      Bold: 750
  Bold: 700                          Bold: 700
                                     NewWeight: 850  ← Uses package default
```

## 📚 Additional Resources

- **DSSketch Format**: See `CLAUDE.md` for full DSSketch syntax
- **Label-Based Syntax**: See `README.md` → "Label-Based Syntax" section
- **Standards Class**: `src/dssketch/core/mappings.py`
- **DataManager**: `src/dssketch/config.py`
- **DiscreteAxisHandler**: `src/dssketch/utils/discrete.py`
- **YAML Syntax**: https://yaml.org/spec/1.2/spec.html
- **DesignSpace Spec**: https://github.com/fonttools/fonttools/tree/master/Doc/source/designspaceLib

## ❓ FAQ

**Q: Do I need to restart after changing data files?**
A: No, data files are loaded on-demand. Just run your conversion again.

**Q: Can I merge user and package data?**
A: No, user files completely replace package files. Copy the package file and modify it.

**Q: What happens if I have invalid YAML?**
A: DSSketchLogger will show a warning and fall back to package defaults.

**Q: Can I use custom data in Python scripts?**
A: Yes! Use `get_data_manager().load_data_file()` or convenience functions.

**Q: How do I share custom mappings with my team?**
A: Use `DSSKETCH_DATA_DIR` to point to a project directory and commit it to git.


---

**DSSketch Data Customization makes variable font development flexible and team-friendly. 🎨**
