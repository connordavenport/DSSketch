#!/usr/bin/env python3
"""
DesignSpace Sketch CLI
Command-line interface for converting between .dssketch and .designspace formats
"""

import argparse
from pathlib import Path

# Import all necessary components from dssketch module
from dssketch import (
    DSSParser,
    DSSWriter,
    DSSToDesignSpace,
    DesignSpaceToDSS,
    UFOValidator
)


def main():
    """Command-line interface for DesignSpace Sketch"""
    parser = argparse.ArgumentParser(
        prog='dssketch',
        description='DesignSpace Sketch - Convert between .dssketch and .designspace formats\n'
                   'UFO validation and DSSketch optimization are enabled by default.'
    )
    parser.add_argument('input', help='Input file (.dssketch or .designspace)')
    parser.add_argument('-o', '--output', help='Output file (optional)')
    parser.add_argument('--format', choices=['dssketch', 'dss', 'designspace', 'auto'], 
                       default='auto', help='Output format (dss is alias for dssketch)')
    parser.add_argument('--no-validation', action='store_true',
                       help='Skip UFO file validation (not recommended)')
    parser.add_argument('--allow-missing-ufos', action='store_true',
                       help='Continue conversion even if UFO files are missing')
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    
    if not input_path.exists():
        print(f"Error: Input file {input_path} does not exist")
        return 1
    
    try:
        # Determine output format
        output_format = args.format
        if output_format == 'auto':
            # Auto-detect based on input extension
            if input_path.suffix.lower() in ['.dssketch', '.dss']:
                output_format = 'designspace'
            elif input_path.suffix.lower() == '.designspace':
                output_format = 'dssketch'
            else:
                print(f"Error: Cannot auto-detect format for {input_path.suffix}")
                print("Supported input formats: .dssketch, .dss, .designspace")
                print("Use --format to specify output format explicitly")
                return 1
        
        # Normalize dss to dssketch
        if output_format == 'dss':
            output_format = 'dssketch'
        
        # Determine conversion direction
        if output_format == 'designspace':
            # Convert to DesignSpace
            if input_path.suffix.lower() in ['.dssketch', '.dss']:
                parser = DSSParser()
                dss_doc = parser.parse_file(str(input_path))
                
                # Validate UFO files by default
                if not args.no_validation:
                    validation_report = UFOValidator.validate_ufo_files(dss_doc, str(input_path))
                    
                    # Print validation results
                    if validation_report.has_errors:
                        print("❌ UFO Validation Errors:")
                        for error in validation_report.path_errors:
                            print(f"  - Path error: {error}")
                        for missing in validation_report.missing_files:
                            print(f"  - Missing UFO: {missing}")
                        for invalid in validation_report.invalid_ufos:
                            print(f"  - Invalid UFO: {invalid}")
                        
                        # Fail by default unless --allow-missing-ufos is used
                        if not args.allow_missing_ufos:
                            print("\n💡 Use --allow-missing-ufos to continue despite validation errors")
                            return 1
                    
                    if validation_report.has_warnings:
                        print("⚠️  UFO Validation Warnings:")
                        for warning in validation_report.warnings:
                            print(f"  - {warning}")
                    
                    if not validation_report.has_errors and not validation_report.has_warnings:
                        print("✅ All UFO files validated successfully")
                
                # Determine base path for UFO files (same logic as UFOValidator)
                dssketch_dir = input_path.parent
                
                # Always use the dssketch file directory as base_path
                # because the source filenames already include any path prefix
                base_path = dssketch_dir
                
                converter = DSSToDesignSpace(base_path)
                ds_doc = converter.convert(dss_doc)
                
                output_path = args.output or input_path.with_suffix('.designspace')
                ds_doc.write(str(output_path))
                print(f"Converted {input_path} -> {output_path}")
            else:
                print(f"Error: Cannot convert {input_path.suffix} to .designspace")
                print("Input must be .dssketch file for conversion to .designspace")
                return 1
            
        elif output_format == 'dssketch':
            # Convert to DSSketch/DSS
            if input_path.suffix.lower() == '.designspace':
                converter = DesignSpaceToDSS()
                dss_doc = converter.convert_file(str(input_path))
                
                # Load DesignSpace document for glyph validation
                from fontTools.designspaceLib import DesignSpaceDocument
                ds_doc = DesignSpaceDocument.fromfile(str(input_path))
                
                writer = DSSWriter(optimize=True, ds_doc=ds_doc, base_path=str(input_path.parent))  # Always optimize
                dss_content = writer.write(dss_doc)
                
                output_path = args.output or input_path.with_suffix('.dssketch')
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(dss_content)
                print(f"Converted {input_path} -> {output_path}")
            else:
                print(f"Error: Cannot convert {input_path.suffix} to .dssketch")
                print("Input must be .designspace file for conversion to .dssketch")
                return 1
            
        else:
            print(f"Error: Unknown output format: {output_format}")
            print("Supported formats: dssketch, dss, designspace, auto")
            return 1
            
    except Exception as e:
        import traceback
        print(f"Error during conversion: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())