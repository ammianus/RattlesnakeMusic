#!/usr/bin/env python3
r"""
Music Library Metadata Validator
A CLI tool to scan music directories and validate metadata in MP3 and MP4 files.
"""

import os
import sys
import argparse
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional
import json
from datetime import datetime

try:
    from mutagen import File
    from mutagen.id3 import ID3NoHeaderError
    from mutagen.mp3 import MP3
    from mutagen.mp4 import MP4, MP4Cover
except ImportError:
    print("Error: Required 'mutagen' library not found.")
    print("Please install it with: pip install mutagen")
    sys.exit(1)


@dataclass
class ValidationResult:
    """Represents validation results for a single file."""
    filepath: str
    file_type: str
    missing_album_art: bool = False
    missing_album: bool = False
    missing_artist: bool = False
    missing_track_number: bool = False
    error_message: Optional[str] = None

    @property
    def has_issues(self) -> bool:
        """Returns True if any metadata is missing."""
        return any([
            self.missing_album_art,
            self.missing_album,
            self.missing_artist,
            self.missing_track_number
        ])

    @property
    def missing_fields(self) -> List[str]:
        """Returns list of missing metadata fields."""
        fields = []
        if self.missing_album_art:
            fields.append("Album Artwork")
        if self.missing_album:
            fields.append("Album")
        if self.missing_artist:
            fields.append("Artist")
        if self.missing_track_number:
            fields.append("Track Number")
        return fields


class MusicValidator:
    """Main validator class for music files."""
    
    SUPPORTED_EXTENSIONS = {'.mp3', '.mp4', '.m4a'}
    
    def __init__(self):
        self.results: List[ValidationResult] = []
    
    def scan_directory(self, directory: Path, recursive: bool = True) -> None:
        """Scan directory for music files and validate metadata."""
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        if not directory.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {directory}")
        
        pattern = "**/*" if recursive else "*"
        
        for file_path in directory.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                result = self._validate_file(file_path)
                self.results.append(result)
    
    def _validate_file(self, file_path: Path) -> ValidationResult:
        """Validate metadata for a single music file."""
        result = ValidationResult(
            filepath=str(file_path),
            file_type=file_path.suffix.lower()
        )
        
        try:
            audio_file = File(file_path)
            
            if audio_file is None:
                result.error_message = "Unable to read file or unsupported format"
                return result
            
            if file_path.suffix.lower() == '.mp3':
                self._validate_mp3(audio_file, result)
            elif file_path.suffix.lower() in ['.mp4', '.m4a']:
                self._validate_mp4(audio_file, result)
                
        except Exception as e:
            result.error_message = f"Error reading file: {str(e)}"
        
        return result
    
    def _validate_mp3(self, audio_file: MP3, result: ValidationResult) -> None:
        """Validate MP3 file metadata."""
        # Check for album artwork
        has_artwork = False
        if hasattr(audio_file, 'tags') and audio_file.tags:
            # Check for APIC (Attached Picture) frames
            apic_frames = [key for key in audio_file.tags.keys() if key.startswith('APIC')]
            has_artwork = len(apic_frames) > 0
        
        result.missing_album_art = not has_artwork
        
        # Check basic metadata
        if not audio_file.tags:
            result.missing_album = True
            result.missing_artist = True
            result.missing_track_number = True
            return
        
        # Album
        album = audio_file.tags.get('TALB')  # Album title
        result.missing_album = not (album and str(album).strip())
        
        # Artist
        artist = audio_file.tags.get('TPE1')  # Lead artist
        result.missing_artist = not (artist and str(artist).strip())
        
        # Track number
        track = audio_file.tags.get('TRCK')  # Track number
        result.missing_track_number = not (track and str(track).strip())
    
    def _validate_mp4(self, audio_file: MP4, result: ValidationResult) -> None:
        """Validate MP4/M4A file metadata."""
        # Check for album artwork
        has_artwork = 'covr' in audio_file.tags if audio_file.tags else False
        result.missing_album_art = not has_artwork
        
        if not audio_file.tags:
            result.missing_album = True
            result.missing_artist = True
            result.missing_track_number = True
            return
        
        # Album
        album = audio_file.tags.get('\xa9alb')  # Album
        result.missing_album = not (album and album[0].strip() if album else False)
        
        # Artist
        artist = audio_file.tags.get('\xa9ART')  # Artist
        result.missing_artist = not (artist and artist[0].strip() if artist else False)
        
        # Track number
        track = audio_file.tags.get('trkn')  # Track number
        result.missing_track_number = not (track and track[0][0] > 0 if track else False)
    
    def generate_report(self, output_format: str = 'text', condensed: bool = False) -> str:
        """Generate validation report in specified format."""
        if output_format.lower() == 'json':
            return self._generate_json_report()
        elif condensed:
            return self._generate_condensed_report()
        else:
            return self._generate_text_report()
    
    def _generate_text_report(self) -> str:
        """Generate human-readable text report."""
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("MUSIC LIBRARY METADATA VALIDATION REPORT")
        report_lines.append("=" * 60)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Total files scanned: {len(self.results)}")
        
        # Summary statistics
        files_with_issues = [r for r in self.results if r.has_issues]
        files_with_errors = [r for r in self.results if r.error_message]
        
        report_lines.append(f"Files with metadata issues: {len(files_with_issues)}")
        report_lines.append(f"Files with read errors: {len(files_with_errors)}")
        report_lines.append("")
        
        # Detailed results for files with issues
        if files_with_issues:
            report_lines.append("FILES WITH MISSING METADATA:")
            report_lines.append("-" * 40)
            
            for result in files_with_issues:
                report_lines.append(f"\nFile: {result.filepath}")
                report_lines.append(f"Type: {result.file_type.upper()}")
                report_lines.append(f"Missing: {', '.join(result.missing_fields)}")
        
        # Error files
        if files_with_errors:
            report_lines.append("\n\nFILES WITH READ ERRORS:")
            report_lines.append("-" * 40)
            
            for result in files_with_errors:
                report_lines.append(f"\nFile: {result.filepath}")
                report_lines.append(f"Error: {result.error_message}")
        
        # Summary by issue type
        report_lines.append("\n\nSUMMARY BY ISSUE TYPE:")
        report_lines.append("-" * 40)
        
        missing_counts = {
            'Album Artwork': sum(1 for r in self.results if r.missing_album_art),
            'Album': sum(1 for r in self.results if r.missing_album),
            'Artist': sum(1 for r in self.results if r.missing_artist),
            'Track Number': sum(1 for r in self.results if r.missing_track_number),
        }
        
        for issue_type, count in missing_counts.items():
            if count > 0:
                report_lines.append(f"{issue_type}: {count} files")
        
        return "\n".join(report_lines)
    
    def _generate_json_report(self) -> str:
        """Generate JSON format report."""
        report_data = {
            'generated': datetime.now().isoformat(),
            'total_files': len(self.results),
            'files_with_issues': len([r for r in self.results if r.has_issues]),
            'files_with_errors': len([r for r in self.results if r.error_message]),
            'summary': {
                'missing_album_art': sum(1 for r in self.results if r.missing_album_art),
                'missing_album': sum(1 for r in self.results if r.missing_album),
                'missing_artist': sum(1 for r in self.results if r.missing_artist),
                'missing_track_number': sum(1 for r in self.results if r.missing_track_number),
            },
            'files': []
        }
        
        for result in self.results:
            if result.has_issues or result.error_message:
                file_data = {
                    'filepath': result.filepath,
                    'file_type': result.file_type,
                    'missing_metadata': result.missing_fields,
                    'error': result.error_message
                }
                report_data['files'].append(file_data)
        
        return json.dumps(report_data, indent=2)
    
    def _generate_condensed_report(self) -> str:
        """Generate condensed text report showing only files missing album art."""
        files_missing_art = [r for r in self.results if r.missing_album_art and not r.error_message]
        
        report_lines = []
        
        # Add each file missing artwork on its own line
        for result in files_missing_art:
            report_lines.append(result.filepath)
        
        # Add total count at the end
        report_lines.append(f"Total files missing album artwork: {len(files_missing_art)}")
        
        return "\n".join(report_lines)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Validate metadata in music library files (MP3, MP4)',
        epilog=r'Example: python music_validator.py C:\path\to\music --output report.txt'
    )
    
    parser.add_argument(
        'directory',
        type=str,
        help='Directory path to scan for music files'
    )
    
    parser.add_argument(
        '--recursive', '-r',
        action='store_true',
        default=True,
        help='Scan subdirectories recursively (default: True)'
    )
    
    parser.add_argument(
        '--no-recursive',
        action='store_true',
        help='Disable recursive scanning'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output file path (default: print to console)'
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    
    parser.add_argument(
        '--condensed', '-c',
        action='store_true',
        help='Generate condensed report showing only files missing album artwork (one file per line)'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress progress messages'
    )
    
    args = parser.parse_args()
    
    # Handle recursive flag
    recursive = args.recursive and not args.no_recursive
    
    try:
        directory = Path(args.directory).resolve()
        
        if not args.quiet:
            print(f"Scanning directory: {directory}")
            print(f"Recursive: {recursive}")
            print("Processing files...")
        
        validator = MusicValidator()
        validator.scan_directory(directory, recursive=recursive)
        
        if not args.quiet:
            print(f"Scanned {len(validator.results)} files")
        
        # Generate report
        report = validator.generate_report(args.format, condensed=args.condensed)
        
        # Output report
        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            
            if not args.quiet:
                print(f"Report saved to: {output_path}")
                
                # Print count summary for condensed reports
                if args.condensed:
                    missing_art_count = sum(1 for r in validator.results if r.missing_album_art and not r.error_message)
                    print(f"Files missing album artwork: {missing_art_count}")
        else:
            print(report)
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()