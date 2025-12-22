# DSSketch avar2 Specification (Draft)

This document describes the proposed syntax for representing avar2 (axis variations version 2) mappings in the DSSketch format, with full bidirectional conversion support to/from DesignSpace XML.

## Overview

avar2 enables complex many-to-many relationships between input axis values (user-controlled) and output axis values (internal font coordinates). This is essential for:

- **Parametric fonts**: User axes (opsz, wght, wdth) control hidden parametric axes
- **Distortion corrections**: Adjusting interpolation at specific axis combinations
- **HOI (Higher Order Interpolation)**: Animation and complex axis relationships

## Reference Documents

- [avar2 in DesignSpace proposal](https://github.com/fonttools/fonttools/issues/2430)
- OpenType avar table specification
- Real-world examples: AmstelvarA2, RobotoDelta

---

## Syntax Specification

### 1. Hidden Axes Declaration

Hidden axes (not exposed to users) are declared in a separate `axes hidden` section:

```dssketch
axes
    opsz 8:14:144
        Text > 14
        Display > 144
    wght 100:400:1000
        Thin > 100
        Regular > 400 @elidable
        Black > 1000
    wdth 50:100:125
        Condensed > 50
        Normal > 100 @elidable
        Extended > 125

axes hidden
    XOUC 4:90:310
    XOLC 4:85:293
    XOFI 4:88:302
    XTUC 72:400:668
    XTUR 58:561:907
    YTUC 541:750:875
    YTDE -310:-240:-100
    YHAU 0:18:68
```

**Rules:**
- Hidden axes use the same `min:default:max` format as regular axes
- Hidden axes do NOT have label mappings (no `Label > value` lines)
- Hidden axes are marked with `hidden="1"` in DesignSpace XML output
- Custom axis tags (UPPERCASE) are typical for hidden parametric axes

---

### 2. Variables Declaration (`avar2 vars`)

Variables define reusable values for frequently repeated numbers:

```dssketch
avar2 vars
    $YTUC = 750
    $YTDE = -240
    $YHAU = 18
    $YHAL = 18
    $YHAF = 18
    $display_base = 84
    $my_custom_value = 123.5
```

**Rules:**
- Variable names start with `$`
- Names can contain letters, numbers, underscores (e.g., `$YTUC`, `$my_value_1`)
- Values are numeric (integer or float, positive or negative)
- Variables are global scope within the DSSketch file
- Variables can be used in `avar2` and `avar2 matrix` sections
- Undefined variable reference is a parsing error

**Benefits:**
- Single point of change for values repeated 100+ times
- Self-documenting (meaningful names instead of magic numbers)
- Reduces file size and improves readability

---

### 3. Simple Mappings (`avar2`)

For mappings with few output axes:

```dssketch
avar2
    # With description name
    "display_basic" [opsz=Display] > XOUC=84, XOLC=78, YTUC=$YTUC

    # Without name
    [opsz=Display, wdth=Extended] > XOUC=86, XOLC=80, XTUC=540

    # Multi-line format for many outputs
    "display_full" [opsz=Display] > {
        XOUC=84, XOLC=78, XOFI=80,
        XTUC=348, XTUR=470, XTUD=410,
        YTUC=$YTUC, YTDE=$YTDE, YHAU=$YHAU
    }

    # Label-based input coordinates
    [weight=Bold, width=Condensed] > XOPQ=150, YOPQ=85

    # Numeric input coordinates
    [opsz=100, wght=700] > XOUC=90, XOLC=85
```

**Syntax:**
```
["name"] [input_conditions] > output_assignments
```

**Input conditions:**
- Format: `axis=value` or `axis=Label`
- Multiple conditions separated by `, `
- Supports both axis tags (`opsz`, `wght`) and names (`Optical size`, `Weight`)
- Supports both numeric values and label names from axis mappings

**Output assignments:**
- Format: `AXIS=value` or `AXIS=$variable`
- Multiple assignments separated by `, `
- Use `{ }` for multi-line format

---

### 4. Matrix Format (`avar2 matrix`)

For mappings with many output axes (10+), matrix format is more compact:

```dssketch
avar2 matrix "parametric_horizontal"
    outputs  XOUC XOLC XOFI XTUC XTUR XTUD XTLC XTLR

    [opsz=Display]                        84   78   80  348  470  410  224  308
    [opsz=Display, wdth=Extended]         86   80   79  540  702  600  414  502
    [opsz=Display, wdth=Condensed]        78   71   72  168  214  242  106  140
    [opsz=Display, wght=Thin]             34   34   30  418  571  433  288  402
    [opsz=Display, wght=Black]           244  234  237  198  251  306  151  175
```

**Syntax:**
```
avar2 matrix ["name"]
    outputs  AXIS1 AXIS2 AXIS3 ...

    [input_conditions]  value1 value2 value3 ...
```

**Rules:**
- Matrix name is optional but recommended for documentation
- `outputs` line defines column order (whitespace-separated axis tags)
- Each data row: `[input]` followed by whitespace-separated values
- Values aligned by position with `outputs` columns
- Values can be numbers or `$variables`
- Whitespace between values is flexible (spaces/tabs for alignment)

**With variables:**
```dssketch
avar2 matrix "with_constants"
    outputs  XOUC XOLC YTUC  YTDE  YHAU

    [opsz=Display]                  84   78  $YTUC $YTDE $YHAU
    [opsz=Display, wdth=Extended]   86   80  $YTUC $YTDE $YHAU
    [opsz=Text]                     90   85    541  -310     0
```

---

### 5. Multiple Sections and Overlay

Multiple `avar2` and `avar2 matrix` sections can coexist and overlay:

```dssketch
# Base matrix - horizontal parametric axes
avar2 matrix "horizontal"
    outputs  XOUC XOLC XOFI XTUC XTUR

    [opsz=Display]   84   78   80  348  470
    [opsz=Text]      90   85   88  400  561

# Additional matrix - vertical axes (overlays on same inputs)
avar2 matrix "vertical"
    outputs  YTUC YTLC YTAS YTDE

    [opsz=Display]  $YTUC  471  756  $YTDE
    [opsz=Text]     $YTUC  511  767  $YTDE

# Simple mappings - additional axes
avar2
    [opsz=Display] > YHAU=$YHAU, YHAL=$YHAL, YHAF=$YHAF
    [opsz=Text] > YHAU=$YHAU, YHAL=$YHAL, YHAF=$YHAF
```

**Overlay rules:**
1. First section is base
2. Subsequent sections add new output axes to existing inputs
3. If same output axis appears multiple times for same input: **last value wins** + warning in log
4. All sections merged into single `<mapping>` elements in DesignSpace output

---

## DesignSpace XML Mapping

### DSSketch to DesignSpace

```dssketch
avar2 vars
    $YTUC = 750

avar2
    "display" [opsz=Display] > XOUC=84, YTUC=$YTUC
```

Converts to:

```xml
<axes>
    <!-- regular axes -->
    <axis tag="opsz" name="Optical size" minimum="8" maximum="144" default="14">
        <!-- avar1 maps if any -->
    </axis>

    <!-- hidden axes -->
    <axis tag="XOUC" name="XOUC" minimum="4" maximum="310" default="90" hidden="1"/>
    <axis tag="YTUC" name="YTUC" minimum="541" maximum="875" default="750" hidden="1"/>

    <mappings>
        <mapping description="display">
            <input>
                <dimension name="Optical size" xvalue="144"/>
            </input>
            <output>
                <dimension name="XOUC" xvalue="84"/>
                <dimension name="YTUC" xvalue="750"/>
            </output>
        </mapping>
    </mappings>
</axes>
```

### DesignSpace to DSSketch

The converter should:
1. Detect hidden axes (`hidden="1"`) and place in `axes hidden` section
2. Analyze output values for repetition patterns
3. Auto-generate `avar2 vars` for values repeated 3+ times
4. Choose matrix format when mapping has 6+ output dimensions
5. Preserve `description` attribute as mapping name

---

## Complete Example

```dssketch
family Amstelvar
suffix VF

axes
    opsz 8:14:144
        Text > 14
        Display > 144
    wght 100:400:1000
        Thin > 100
        Regular > 400 @elidable
        Black > 1000
    wdth 50:100:125
        Condensed > 50
        Normal > 100 @elidable
        Extended > 125

axes hidden
    XOUC 4:90:310
    XOLC 4:85:293
    XOFI 4:88:302
    XTUC 72:400:668
    XTUR 58:561:907
    XTUD 50:410:705
    XTLC 42:243:500
    XTLR 46:337:625
    YTUC 541:750:875
    YTLC 436:511:594
    YTAS 665:767:875
    YTDE -310:-240:-100
    YHAU 0:18:68
    YHAL 0:18:42
    YHAF 0:18:68

avar2 vars
    $YTUC = 750
    $YTDE = -240
    $YHAU = 18
    $YHAL = 18
    $YHAF = 18
    $YTAS = 756

avar2 matrix "opsz_display_horizontal"
    outputs  XOUC XOLC XOFI XTUC XTUR XTUD XTLC XTLR

    [opsz=Display]                        84   78   80  348  470  410  224  308
    [opsz=Display, wdth=Extended]         86   80   79  540  702  600  414  502
    [opsz=Display, wdth=Condensed]        78   71   72  168  214  242  106  140
    [opsz=Display, wght=Thin]             34   34   30  418  571  433  288  402
    [opsz=Display, wght=Black]           244  234  237  198  251  306  151  175
    [opsz=Display, wght=Black, wdth=Ext] 246  237  236  390  483  504  341  369
    [opsz=Display, wght=Black, wdth=Cnd] 239  228  229   72   66  170   46   49

avar2 matrix "opsz_display_vertical"
    outputs  YTUC  YTLC YTAS  YTDE  YHAU YHAL YHAF

    [opsz=Display]                       $YTUC  471 $YTAS $YTDE $YHAU $YHAL $YHAF
    [opsz=Display, wdth=Extended]        $YTUC  470 $YTAS $YTDE $YHAU $YHAL $YHAF
    [opsz=Display, wdth=Condensed]       $YTUC  468 $YTAS  -230 $YHAU $YHAL $YHAF
    [opsz=Display, wght=Thin]            $YTUC  471   748  -230 $YHAU   14    10
    [opsz=Display, wght=Black]           $YTUC  496 $YTAS  -230 $YHAU $YHAL $YHAF
    [opsz=Display, wght=Black, wdth=Ext] $YTUC  496 $YTAS  -230 $YHAU $YHAL $YHAF
    [opsz=Display, wght=Black, wdth=Cnd] $YTUC  495 $YTAS  -230 $YHAU $YHAL $YHAF

sources [opsz, wght, wdth]
    Amstelvar-Roman [Text, Regular, Normal] @base

instances auto
```

---

## Implementation Notes

### Parser Requirements

1. **New sections to parse:**
   - `axes hidden` - same syntax as `axes` but without label mappings
   - `avar2 vars` - variable definitions
   - `avar2` - simple mappings
   - `avar2 matrix` - matrix format mappings

2. **Variable resolution:**
   - First pass: collect all `$variable = value` definitions
   - Second pass: resolve `$variable` references in avar2 sections
   - Error if undefined variable referenced

3. **Matrix parsing:**
   - Parse `outputs` line to get column axis order
   - Split data rows by whitespace
   - Match values to columns by position
   - Support mixed numbers and `$variables`

4. **Overlay merging:**
   - Track all mappings by input signature
   - Merge outputs from multiple sections
   - Log warning on conflicts, keep last value

### Writer Requirements

1. **Hidden axes detection:**
   - Check `hidden="1"` attribute in DesignSpace
   - Write to `axes hidden` section

2. **Variable extraction:**
   - Analyze all output values across mappings
   - Identify values repeated 3+ times
   - Generate `$AXIS_value` or meaningful names
   - Replace repeated values with variables

3. **Format selection:**
   - Use matrix format when mapping has 6+ output dimensions
   - Use simple format for 1-5 output dimensions
   - Group matrices by common output axes

4. **Optimization:**
   - Detect overlayable matrices (same inputs, different outputs)
   - Split large matrices for readability

---

## Open Questions

1. **avar1 + avar2 coexistence:** How to handle fonts with both? Keep avar1 maps inside `axes` as current DSSketch syntax.

2. **Negative axis values:** Fully supported (e.g., `YTDE -310:-240:-100`).

3. **Delta mode:** Not implemented in v1. May add `mode="delta"` later if real use cases emerge.

4. **Variable arithmetic:** Not supported in v1. Variables are simple value substitution only.

---

## Version History

- **v0.1 (2024-12):** Initial draft specification based on AmstelvarA2 and RobotoDelta analysis.
