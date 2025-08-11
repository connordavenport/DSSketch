#!/usr/bin/env python3
"""
DesignSpace Sketch CLI
Command-line interface for converting between .dssketch and .designspace formats
"""

import argparse
from pathlib import Path

from src.dssketch import (
    DesignSpaceToDSS,
    DSSParser,
    DSSToDesignSpace,
    DSSWriter,
    UFOValidator,
)


def main():
    """Simplified CLI for DesignSpace Sketch conversion"""
    parser = argparse.ArgumentParser(
        prog='dssketch',
        description='Simple converter between .dssketch and .designspace formats\n'
                   'Automatically detects input format and converts to the other format.'
    )
    parser.add_argument('input', help='Input file (.dssketch or .designspace)')
    parser.add_argument('-o', '--output', help='Output file (optional, defaults to same directory)')

    args = parser.parse_args()

    input_path = Path(args.input)

    if not input_path.exists():
        print(f"Error: Input file {input_path} does not exist")
        return 1

    try:
        # Auto-detect output format based on input extension
        if input_path.suffix.lower() in ['.dssketch', '.dss']:
            output_format = 'designspace'
        elif input_path.suffix.lower() == '.designspace':
            output_format = 'dssketch'
        else:
            print(f"Error: Unsupported input format {input_path.suffix}")
            print("Supported formats: .dssketch, .dss, .designspace")
            return 1

        # Convert based on detected format
        if output_format == 'designspace':
            # Convert .dssketch/.dss to .designspace
            parser = DSSParser()
            dss_doc = parser.parse_file(str(input_path))

            # Simple UFO validation with basic error handling
            validation_report = UFOValidator.validate_ufo_files(dss_doc, str(input_path))
            if validation_report.has_errors:
                print("⚠️  Some UFO files may be missing or invalid, but continuing conversion...")

            base_path = input_path.parent
            converter = DSSToDesignSpace(base_path)
            ds_doc = converter.convert(dss_doc)

            output_path = Path(args.output) if args.output else input_path.with_suffix('.designspace')
            ds_doc.write(str(output_path))
            print(f"✅ Converted {input_path.name} -> {output_path.name}")

        elif output_format == 'dssketch':
            # Convert .designspace to .dssketch
            converter = DesignSpaceToDSS()
            dss_doc = converter.convert_file(str(input_path))

            # Load DesignSpace document for glyph validation
            from fontTools.designspaceLib import DesignSpaceDocument
            ds_doc = DesignSpaceDocument.fromfile(str(input_path))

            writer = DSSWriter(optimize=True, ds_doc=ds_doc, base_path=str(input_path.parent))
            dss_content = writer.write(dss_doc)

            output_path = Path(args.output) if args.output else input_path.with_suffix('.dssketch')
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(dss_content)
            print(f"✅ Converted {input_path.name} -> {output_path.name}")

    except Exception as e:
        import traceback
        print(f"Error during conversion: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
