# DesignSpace Rules to DSSketch Conversion

This document explains how substitution rules are converted from DesignSpace XML format to the compact DSSketch format.

## Overview

DesignSpace rules control glyph substitutions based on axis conditions (weight, width, etc.). DSSketch provides a more compact syntax while preserving full functionality.

## Conversion Process

### 1. Rule Structure Analysis

The converter processes DesignSpace `<rule>` elements from `src/dssketch/converters/designspace_to_dss.py:203` in the `_convert_rule()` method:

```python
def _convert_rule(self, rule: RuleDescriptor, ds_doc: DesignSpaceDocument) -> Optional[DSSRule]:
```

### 2. Substitution Extraction

**DesignSpace format:**
```xml
<rule name="switching dollar">
  <sub name="dollar" with="dollar.heavy"/>
  <sub name="cent" with="cent.heavy"/>
</rule>
```

**Conversion process:**
- Extracts all `<sub>` elements as (from_glyph, to_glyph) pairs
- Stores as `substitutions` list in DSSRule object

### 3. Condition Processing

The converter handles two DesignSpace condition formats:

#### Modern conditionSets format (recommended):
```xml
<rule name="switching dollar">
  <conditionset>
    <condition name="weight" minimum="700" maximum="1000"/>
  </conditionset>
</rule>
```

#### Legacy conditions format (deprecated):
```xml
<rule name="switching dollar">
  <condition name="weight" minimum="700" maximum="1000"/>
</rule>
```

Both are normalized to the same internal format:
```python
conditions = [{
    'axis': 'weight',
    'minimum': 700,
    'maximum': 1000
}]
```

## DSSketch Output Format

### 4. Parentheses Syntax

DSSketch uses a clean, readable syntax that eliminates confusion:

**Syntax:**
```dssketch
rules
    # With explicit name
    cen* dol* > .rvrn (weight >= 480) "switching Dollar"
    
    # Auto-generated name (rule1, rule2, etc.)
    K k > .alt (weight <= 480)
    
    # Multiple conditions
    ampersand > ampersand.fancy (weight >= 600 && width >= 110) "compound rule"
    
    # Range conditions
    g > g.alt (450 <= weight <= 650)
    
    # Exact value conditions
    a > a.italic (italic == 1)
```

**Benefits:**
- **Clear separation:** Parentheses `()` for conditions, quotes `""` for names
- **Auto-generated names:** No need to manually name every rule (rule1, rule2, etc.)
- **Error-free:** Clean syntax without symbol confusion
- **Consistent:** Uniform spacing and formatting

### 5. Condition Formatting (`_format_rule()` at `src/dssketch/writers/dss_writer.py:170`)

The converter generates different condition syntax based on min/max values:

| DesignSpace Condition | DSSketch Output | Description |
|----------------------|-----------------|-------------|
| `minimum="700" maximum="1000"` | `(weight >= 700)` | Maximum >= 1000 treated as infinity |
| `minimum="0" maximum="500"` | `(weight <= 500)` | Minimum of 0 omitted |
| `minimum="400" maximum="600"` | `(400 <= weight <= 600)` | Explicit range |
| `minimum="500" maximum="500"` | `(weight == 500)` | Exact value |

### 6. Pattern Detection and Optimization

The converter attempts to detect patterns in multiple substitutions to create compact wildcard syntax:

**Input (multiple similar substitutions):**
```xml
<sub name="dollar" with="dollar.heavy"/>
<sub name="cent" with="cent.heavy"/>
<sub name="sterling" with="sterling.heavy"/>
```

**Pattern Detection Logic (`_detect_substitution_pattern()` at line 959):**
1. Checks if all substitutions follow same suffix pattern (e.g., `.heavy`)
2. Groups glyphs by common prefixes 
3. Generates wildcard patterns when beneficial

**Compact Output:**
```dssketch
dollar* cent* sterling* > .heavy (weight >= 700) "switching currency"
```

**Fallback (individual lines):**
```dssketch
dollar > dollar.heavy (weight >= 700) "rule1"
cent > cent.heavy (weight >= 700) "rule2"
sterling > sterling.heavy (weight >= 700) "rule3"
```

## Complete Examples

### Example 1: Simple Single Condition

**DesignSpace:**
```xml
<rule name="switching dollar">
  <conditionset>
    <condition name="weight" minimum="700" maximum="1000"/>
  </conditionset>
  <sub name="dollar" with="dollar.heavy"/>
  <sub name="cent" with="cent.heavy"/>
</rule>
```

**DSSketch:**
```dssketch
rules
    dollar > dollar.heavy (weight >= 700)
    cent > cent.heavy (weight >= 700)
```

### Example 2: Compound Conditions

**DesignSpace:**
```xml
<rule name="switching ampersand">
  <conditionset>
    <condition name="weight" minimum="600" maximum="1000"/>
    <condition name="width" minimum="110" maximum="1000"/>
  </conditionset>
  <sub name="ampersand" with="ampersand.fancy"/>
</rule>
```

**DSSketch:**
```dssketch
rules
    ampersand > ampersand.fancy (weight >= 600 && width >= 110) "switching ampersand"
```

### Example 3: Exact Value Condition

**DesignSpace:**
```xml
<rule name="italic switching">
  <conditionset>
    <condition name="italic" minimum="1" maximum="1"/>
  </conditionset>
  <sub name="a" with="a.italic"/>
</rule>
```

**DSSketch:**
```dssketch
rules
    a > a.italic (italic == 1)
```

### Example 4: Range Condition

**DesignSpace:**
```xml
<rule name="mid-weight alternates">
  <conditionset>
    <condition name="weight" minimum="450" maximum="650"/>
  </conditionset>
  <sub name="g" with="g.alt"/>
</rule>
```

**DSSketch:**
```dssketch
rules
    g > g.alt (450 <= weight <= 650)
```

## Advanced Features

### Syntax Implementation

**Parsing (`_parse_rule_line()` at line 1456):**
1. **Pattern matching:** Uses regex `^(.+?)\s*>\s*(.+?)\s*\(([^)]+)\)(?:\s*"([^"]+)")?`
2. **Auto-generated names:** Creates `rule1`, `rule2`, etc. when name is omitted
3. **Error handling:** Shows helpful warnings for invalid syntax

**Pattern Matching:**
```python
# Syntax: pattern > target (condition) "name"
paren_match = re.match(r'^(.+?)\s*>\s*(.+?)\s*\(([^)]+)\)(?:\s*"([^"]+)")?', line)

# Example matches:
# "A a > .alt (weight >= 600)" → groups: ['A a', '.alt', 'weight >= 600', None]
# "dollar* > .rvrn (weight >= 480) "currency"" → groups: ['dollar*', '.rvrn', 'weight >= 480', 'currency']
```

**Condition Parsing (`_parse_condition_string()` at line 1399):**
- Handles range conditions: `400 <= weight <= 700`
- Standard operators: `weight >= 480`, `weight <= 400`, `weight == 500`
- Multiple conditions: `weight >= 600 && width >= 110`

### Rule Names and Comments

**Naming:**
- Explicit names in quotes: `"switching Dollar"`
- Auto-generated names: `rule1`, `rule2`, `rule3` (omitted in output)
- Comments supported: `# This is a comment`

**Name Formatting (`_format_rule_name()` at line 970):**
- Auto-generated names (rule1, rule2, etc.) are omitted from output
- Only explicit, meaningful names are included in generated DSSketch files

### Wildcard Pattern Detection

Current implementation (line ~1100) uses hardcoded glyph lists for pattern detection. Pattern detection looks for:

1. **Common suffix transformations** (e.g., `.heavy`, `.wide`, `.alt`)
2. **Prefix groupings** (e.g., `dollar`, `cent`, `sterling` for currency symbols)
3. **Minimum threshold** (typically 2+ substitutions to justify wildcards)

### Optimization Benefits

DSSketch rules are typically 60-80% more compact than DesignSpace XML:

- **Verbose DesignSpace:** ~15 lines per rule with XML overhead
- **Compact DSSketch:** ~1-3 lines per rule with minimal syntax
- **Pattern optimization:** Multiple similar rules collapsed to single wildcard line

## Implementation Notes

### Key Classes and Methods

**Core Conversion:**
- **`DesignSpaceToDSS._convert_rule()`** (`src/dssketch/converters/designspace_to_dss.py:203`): Main DesignSpace → DSSketch conversion
- **`DSSToDesignSpace._convert_rule()`** (`src/dssketch/converters/dss_to_designspace.py:219`): Main DSSketch → DesignSpace conversion
- **`DSSRule`** (`src/dssketch/core/models.py`): Data structure for rules

**Parsing:**
- **`DSSParser._parse_rule_line()`** (`src/dssketch/parsers/dss_parser.py:402`): Parses parentheses syntax
- **`DSSParser._parse_condition_string()`** (`src/dssketch/parsers/dss_parser.py:351`): Condition parsing
- **`DSSToDesignSpace._expand_wildcard_pattern()`** (`src/dssketch/converters/dss_to_designspace.py:247`): Expands wildcards with target validation

**Output Generation:**
- **`DSSWriter._format_rule()`** (`src/dssketch/writers/dss_writer.py:170`): Generates parentheses syntax
- **`DSSWriter._format_rule_name()`** (`src/dssketch/writers/dss_writer.py:235`): Handles auto-generated name omission
- **`PatternMatcher`** (`src/dssketch/utils/patterns.py`): Wildcard pattern matching

### Axis Name Mapping

The converter recognizes standard axis abbreviations:
- `weight` → `wght`
- `width` → `wdth` 
- `italic` → `ital`
- `slant` → `slnt`
- `optical` → `opsz`

Custom axis names are preserved as-is.

### Critical Issue: Wildcard Pattern Over-Matching

**Problem:** Current wildcard pattern generation can capture unintended glyphs.

**Example:**
```xml
<!-- DesignSpace has only these specific substitutions -->
<sub name="dollar" with="dollar.heavy"/>
<sub name="cent" with="cent.heavy"/>
```

**Current (incorrect) output:**
```dssketch
dollar* > .heavy  # ❌ WRONG! Captures dollar.small, dollar.tabular, etc.
```

**Should be:**
```dssketch
dollar cent > .heavy  # ✅ CORRECT! Only specified glyphs
```

**Root cause:** `_detect_substitution_pattern()` (lines 995-1001) creates prefix wildcards without validating that the pattern expansion matches exactly the original substitution list.

**Solution implemented:** Added validation that wildcard expansion produces the same glyph set as the original substitutions.

**Key changes made:**

**Solution Status:** ✅ **FIXED** - Enhanced validation prevents over-matching wildcards.

**Implementation Details:**

1. **Enhanced `_detect_substitution_pattern()` method** (`src/dssketch/writers/dss_writer.py:241`):
   ```python
   # Validate that wildcard pattern doesn't over-match if we have glyph list
   if available_glyphs and any('*' in p for p in patterns):
       expanded_glyphs = PatternMatcher.find_matching_glyphs(patterns, available_glyphs)
       original_glyphs = set(from_glyphs)
       
       # Only use wildcard if it matches exactly the original glyphs
       if expanded_glyphs == original_glyphs:
           return (from_pattern, common_suffix)
       else:
           # Fall back to explicit listing to ensure exact matching
           explicit_pattern = " ".join(from_glyphs)
           return (explicit_pattern, common_suffix)
   ```

2. **UFO Glyph Extraction** (`src/dssketch/core/validation.py`):
   ```python
   class UFOGlyphExtractor:
       @staticmethod
       def get_all_glyphs_from_sources(sources, base_path):
           # Safely extracts glyph lists from UFO files
   ```

3. **Wildcard Expansion Validation** (`src/dssketch/converters/dss_to_designspace.py:247`):
   ```python
   def _expand_wildcard_pattern(self, dss_rule: DSSRule, doc: DesignSpaceDocument):
       # Validates target glyphs exist before creating substitutions
       if target in all_glyphs:
           substitutions.append((glyph, target))
       else:
           print(f"⚠️  Warning: Skipping substitution {glyph} -> {target}")
   ```

### Benefits of the Fixes

- **Exact precision:** Wildcard patterns now match only the glyphs specified in the original DesignSpace rule
- **Target validation:** Ensures substitution target glyphs exist in UFO files before creating rules
- **Backward compatibility:** Falls back to explicit glyph listing when wildcard would over-match
- **Error resilience:** Gracefully handles missing UFO files or extraction failures
- **Performance:** UFO glyph extraction is cached and only performed when needed

### Behavior Examples

**Before fix:**
```xml
<sub name="dollar" with="dollar.heavy"/>
<sub name="cent" with="cent.heavy"/>
```
→ `dollar* > .heavy` ❌ (could match dollar.small, dollar.tabular, etc.)

**After fix:**
```xml
<sub name="dollar" with="dollar.heavy"/>  
<sub name="cent" with="cent.heavy"/>
```
→ `dollar cent > .heavy` ✅ (matches exactly these glyphs)

**Target glyph validation:**
```dssketch
# DSSketch rule (potentially invalid) - both syntaxes affected
A a > .alt (weight >= 600)  # New syntax
A a > .alt @ weight >= 600  # Legacy syntax
```

**Before target validation:**
- Creates substitutions `A -> A.alt` and `a -> a.alt` regardless of whether `A.alt` and `a.alt` exist
- Results in broken DesignSpace rules that reference non-existent glyphs

**After target validation:**
- Checks UFO files for existence of `A.alt` and `a.alt`
- If missing: `⚠️  Warning: Skipping substitution A -> A.alt - target glyph 'A.alt' not found in UFO files`
- Only creates valid substitutions, preventing broken rules

### Current Capabilities & Limitations

**✅ What works well:**
1. **Smart wildcard validation** - Prevents over-matching with UFO-based validation
2. **Comprehensive syntax support** - Supports range, compound, exact, and simple conditions
3. **Target glyph validation** - Checks existence in UFO files before creating rules
4. **Bidirectional conversion** - Full round-trip preservation of rule functionality
5. **Pattern optimization** - Suffix-based transformations with safety validation

**⚠️ Current limitations:**
1. **Pattern detection** - Currently limited to suffix-based transformations (e.g., `.rvrn`, `.alt`)
2. **UFO dependency for wildcards** - Wildcard validation requires UFO files to be present
3. **Complex boolean logic** - Only supports AND (`&&`) operations, not OR or NOT
4. **Rule ordering** - Preserved but not optimized for efficiency

## Testing

Test the conversion with provided examples:

```bash
# Convert DesignSpace to DSSketch (generates parentheses syntax)
dssketch examples/KazimirText-Variable-original.designspace

# Test DSSketch to DesignSpace conversion with wildcard expansion  
dssketch examples/KazimirText-Variable-original.dssketch

# Test complex rules with various condition types
dssketch examples/test-rules-complex.dssketch
```

**Example New Syntax Output:**
```dssketch
rules
    # Clean, readable syntax
    cen* dol* > .rvrn (weight >= 480) "switching Dollar"
    K k > .alt (weight <= 480) "switching K"
    
    # Auto-generated names for unnamed rules
    dollar > dollar.small (weight <= 300)
    cent euro > .tabular (width >= 110 && weight >= 500)
```

The bidirectional conversion ensures that all rule functionality is preserved while providing significant size reduction and improved readability. The parentheses syntax eliminates parsing errors and provides clean, maintainable rule definitions.