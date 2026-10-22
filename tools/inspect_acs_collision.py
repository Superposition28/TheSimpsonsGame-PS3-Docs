"""Audit files beneath exact 'collision' path components and walk PS3 ACS records.

Read-only, standard-library research tool. Does not instantiate collision shapes,
infer runtime flags, or require the parent game module to import this file.
Run with --help for local dataset arguments; outputs no proprietary asset bytes.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import struct


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_acs(data: bytes) -> dict:
    """Walk the observed version-1 layout, retaining uninterpreted identifiers."""
    if len(data) < 4 or data[0] != 1 or data[2:4] != b'\0\0':
        raise ValueError('not the observed ACS header: 01 count 00 00')
    offset = 4
    records = []
    for index in range(data[1]):
        if offset + 76 > len(data):
            raise ValueError(f'record {index}: truncated common header')
        size = struct.unpack_from('>I', data, offset)[0]
        if size < 76 or size % 4 or offset + size > len(data):
            raise ValueError(f'record {index}: invalid size {size}')
        raw = data[offset:offset + size]
        transform = list(struct.unpack_from('>12f', raw, 24))
        parameters = list(struct.unpack_from(f'>{(size - 76) // 4}f', raw, 76))
        if not all(math.isfinite(value) for value in transform + parameters):
            raise ValueError(f'record {index}: non-finite float candidate')
        records.append({
            'offset': offset,
            'size': size,
            'identifier_04': raw[4:8].hex(),
            'binding_identifier_08': raw[8:12].hex(),
            'flags_0c_hex': raw[12:16].hex(),
            'word_10_hex': raw[16:20].hex(),
            'identifier_14': raw[20:24].hex(),
            'transform_18_f32be': transform,
            'kind_48': raw[72],
            'kind_padding_49_hex': raw[73:76].hex(),
            'parameters_4c_f32be': parameters,
            'observed_kind_size_pair': (raw[72], size) in ((1, 80), (2, 84), (3, 84)),
        })
        offset += size
    if offset != len(data):
        raise ValueError(f'{len(data) - offset} trailing bytes after declared count')
    return {'header_hex': data[:4].hex(), 'count': data[1], 'records': records}


def audit(flattened_root: Path, canonical_root: Path) -> dict:
    mapping_path = flattened_root / 'normalized_map.json'
    mapping_bytes = mapping_path.read_bytes()
    mapping = json.loads(mapping_bytes)
    by_new: dict[str, list[str]] = {}
    for row in mapping:
        by_new.setdefault(row['new_path'], []).append(row['original_path'])
    paths = sorted(
        (path for path in flattened_root.rglob('*') if path.is_file()
         and 'collision' in [part.lower() for part in path.relative_to(flattened_root).parts[:-1]]),
        key=lambda path: path.relative_to(flattened_root).as_posix(),
    )
    files = []
    unique_acs: dict[str, dict] = {}
    suffix_counts: Counter[str] = Counter()
    kind_counts: Counter[int] = Counter()
    size_counts: Counter[int] = Counter()
    record_sizes: Counter[int] = Counter()
    transform_counts: Counter[tuple[float, ...]] = Counter()
    for path in paths:
        relative = path.relative_to(flattened_root).as_posix()
        candidates = by_new.get(relative, [])
        if len(candidates) != 1:
            raise ValueError(f'{relative}: expected one canonical mapping, got {candidates}')
        canonical = candidates[0]
        data = path.read_bytes()
        digest = sha256(data)
        canonical_data = (canonical_root / canonical).read_bytes()
        if canonical_data != data:
            raise ValueError(f'{relative}: canonical counterpart differs')
        suffix = '.'.join(path.name.split('.')[-2:])
        suffix_counts[suffix] += 1
        entry = {'flattened': relative, 'canonical': canonical,
                 'suffix': suffix, 'size': len(data), 'sha256': digest,
                 'canonical_bytes_equal': True}
        files.append(entry)
        if suffix == 'acs.PS3':
            parsed = parse_acs(data)
            unique_acs.setdefault(digest, {'example_canonical': canonical, **parsed})
            size_counts[len(data)] += 1
            for record in parsed['records']:
                kind_counts[record['kind_48']] += 1
                record_sizes[record['size']] += 1
                transform_counts[tuple(record['transform_18_f32be'])] += 1
    return {
        'schema_version': 1,
        'inspection_date': '2026-10-22',
        'authority': 'local extracted artifact bytes; no original runtime execution',
        'scope': 'Every file beneath an exact case-insensitive collision directory component in ps3-eu-flattened; this set equals the 401 user-supplied paths.',
        'source_ids': ['ps3-eu-extracted', 'ps3-eu-flattened'],
        'mapping_sha256': sha256(mapping_bytes),
        'mapping_entries': len(mapping),
        'flattened_relative_paths_sha256': sha256(('\n'.join(row['flattened'] for row in files) + '\n').encode()),
        'file_count': len(files),
        'suffix_counts': dict(sorted(suffix_counts.items())),
        'acs_summary': {
            'unique_sha256_count': len(unique_acs),
            'file_size_counts': dict(sorted(size_counts.items())),
            'record_size_counts_including_duplicate_files': dict(sorted(record_sizes.items())),
            'kind_counts_including_duplicate_files': dict(sorted(kind_counts.items())),
            'transform_counts_including_duplicate_files': [
                {'values_f32be': list(values), 'count': count}
                for values, count in sorted(transform_counts.items())
            ],
            'all_records_end_at_eof': True,
        },
        'limitations': [
            'Directory-name scope excludes other physics files elsewhere in the game tree.',
            'The map describes the processed Full and FullFlattened datasets, not original STR membership.',
            'Record walking is structural validation, not proof of shape semantics, flags, units, or bone-to-mesh transforms.',
            'Observed kind-size pairs are reported; future kinds must not be interpreted using this sample schema automatically.',
        ],
        'files': files,
        'acs_by_sha256': unique_acs,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--flattened-root', type=Path, required=True)
    parser.add_argument('--canonical-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.flattened_root, args.canonical_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({key: result[key] for key in ('file_count', 'suffix_counts', 'mapping_sha256')}))
    print(f"ACS: {result['acs_summary']['unique_sha256_count']} unique contents; all declared records end at EOF")


if __name__ == '__main__':
    main()
