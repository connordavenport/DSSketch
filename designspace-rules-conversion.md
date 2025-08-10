# DesignSpace Rules to DSSketch Conversion

This document explains how substitution rules are converted from DesignSpace XML format to the compact DSSketch format.

## Overview

DesignSpace rules control glyph substitutions based on axis conditions (weight, width, etc.). DSSketch provides a more compact syntax while preserving full functionality.

## Conversion Process

### 1. Rule Structure Analysis

The converter processes DesignSpace `<rule>` elements from `dssketch.py:717` in the `_convert_rule()` method:

```python
def _convert_rule(self, rule: RuleDescriptor, ds_doc: DesignSpaceDocument) -> Optional[DSLRule]:
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
- Stores as `substitutions` list in DSLRule object

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

### 5. Condition Formatting (`_format_rule()` at line 905)

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
- **`DesignSpaceToDSL._convert_rule()`** (line 717): Main DesignSpace → DSSketch conversion
- **`DSLToDesignSpace._convert_rule()`** (line 1709): Main DSSketch → DesignSpace conversion
- **`DSLRule`** (line 93): Data structure for rules

**Parsing (New & Legacy):**
- **`DSLParser._parse_rule_line()`** (line 1450): Parses both new parentheses and legacy @ syntax
- **`DSLParser._parse_condition_string()`** (line 1399): Unified condition parsing for both syntaxes
- **`DSLToDesignSpace._expand_wildcard_pattern()`** (line 1748): Expands wildcards with target validation

**Output Generation:**
- **`DSLWriter._format_rule()`** (line 905): Generates new parentheses syntax by default
- **`DSLWriter._format_rule_name()`** (line 970): Handles auto-generated name omission
- **`DSLWriter._detect_substitution_pattern()`** (line 976): Pattern optimization with validation

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

1. **Enhanced `_detect_substitution_pattern()` method** (dssketch.py:959):
   ```python
   def _detect_substitution_pattern(self, substitutions: List[Tuple[str, str]], available_glyphs: Optional[Set[str]] = None) -> Optional[Tuple[str, str]]:
       # ... existing suffix detection logic ...
       
       if patterns and available_glyphs and any('*' in p for p in patterns):
           # Validate that wildcard pattern doesn't over-match
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

2. **Updated DSLWriter constructor** to accept DesignSpace document and base path for glyph extraction:
   ```python
   def __init__(self, optimize: bool = True, ds_doc: Optional[DesignSpaceDocument] = None, base_path: Optional[str] = None)
   ```

3. **Enhanced `_format_rule()` method** to extract glyphs from UFO files when available:
   ```python
   # Extract glyph list from UFO files if DesignSpace document is available
   available_glyphs = None
   if self.ds_doc and self.base_path:
       available_glyphs = UFOGlyphExtractor.get_all_glyphs_from_sources(self.ds_doc, self.base_path)
   ```

4. **Updated CLI** (dssketch_cli.py:127-131) to pass DesignSpace document to writer:
   ```python
   ds_doc = DesignSpaceDocument.fromfile(str(input_path))
   writer = DSLWriter(optimize=True, ds_doc=ds_doc, base_path=str(input_path.parent))
   ```

5. **Enhanced `_expand_wildcard_pattern()` method** (dssketch.py:1748) to validate target glyph existence:
   ```python
   # Validate regular substitutions (non-wildcard)
   for from_glyph, to_glyph in dsl_rule.substitutions:
       if to_glyph in all_glyphs:
           validated_substitutions.append((from_glyph, to_glyph))
       else:
           print(f"⚠️  Warning: Skipping substitution {from_glyph} -> {to_glyph} - target glyph '{to_glyph}' not found in UFO files")
   
   # Also validates wildcard-generated targets
   if target in all_glyphs:
       substitutions.append((glyph, target))
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

### Remaining Limitations

1. **Pattern detection** is currently limited to suffix-based transformations
2. **UFO file dependency:** Requires UFO files to be present for validation
3. **Complex conditions** beyond AND/OR operations are not supported
4. **Rule ordering** is preserved but not optimized

## Testing

Test the conversion with provided examples:

```bash
# Convert DesignSpace to DSSketch (generates new parentheses syntax)
python dssketch_cli.py examples/complex-rules.designspace

# Test new syntax parsing
python dssketch_cli.py examples/KazimirText-Variable-test.dssketch

# Convert back to verify round-trip preservation  
python dssketch_cli.py examples/complex-rules.dsl
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