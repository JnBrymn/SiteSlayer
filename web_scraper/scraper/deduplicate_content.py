"""
Content Deduplication Module

Removes repeated chunks from markdown content files using hash-based deduplication.
This is particularly useful for aggregated website content where navigation menus,
footers, and other elements are repeated across multiple pages.
"""

import hashlib
from collections import defaultdict
from typing import List, Tuple, Dict
import re


def hash_chunk(chunk: str) -> str:
    """Generate a hash for a text chunk."""
    return hashlib.md5(chunk.encode('utf-8')).hexdigest()


def split_into_chunks(content: str, chunk_size: int = 10, overlap: int = 0) -> List[Tuple[str, int, int]]:
    """
    Split content into chunks of specified size (in lines).
    
    Args:
        content: The content to split
        chunk_size: Number of lines per chunk
        overlap: Number of lines to overlap between chunks (for better detection)
    
    Returns:
        List of tuples: (chunk_text, start_line, end_line)
    """
    lines = content.split('\n')
    chunks = []
    
    i = 0
    while i < len(lines):
        end = min(i + chunk_size, len(lines))
        chunk_lines = lines[i:end]
        chunk_text = '\n'.join(chunk_lines)
        
        if chunk_text.strip():  # Only add non-empty chunks
            chunks.append((chunk_text, i, end))
        
        i += chunk_size - overlap if overlap > 0 else chunk_size
    
    return chunks


def find_repeated_chunks(content: str, min_chunk_size: int = 5, min_occurrences: int = 2) -> Dict[str, List[Tuple[int, int]]]:
    """
    Find chunks that appear multiple times in the content.
    
    Args:
        content: The content to analyze
        min_chunk_size: Minimum number of lines in a chunk
        min_occurrences: Minimum number of times a chunk must appear to be considered
    
    Returns:
        Dictionary mapping chunk hash to list of (start_line, end_line) positions
    """
    lines = content.split('\n')
    chunk_hashes = defaultdict(list)
    
    # Try different chunk sizes to catch various patterns
    for chunk_size in range(min_chunk_size, min(min_chunk_size + 20, len(lines) // 2)):
        chunks = split_into_chunks(content, chunk_size=chunk_size, overlap=chunk_size // 2)
        
        for chunk_text, start, end in chunks:
            # Normalize whitespace for better matching
            normalized = re.sub(r'\s+', ' ', chunk_text.strip())
            if len(normalized) < 50:  # Skip very short chunks
                continue
            
            chunk_hash = hash_chunk(normalized)
            chunk_hashes[chunk_hash].append((start, end, chunk_text))
    
    # Filter to only chunks that appear multiple times
    repeated = {}
    for chunk_hash, occurrences in chunk_hashes.items():
        if len(occurrences) >= min_occurrences:
            # Use the first occurrence's text as the canonical version
            _, _, canonical_text = occurrences[0]
            repeated[chunk_hash] = {
                'text': canonical_text,
                'positions': [(start, end) for start, end, _ in occurrences],
                'count': len(occurrences)
            }
    
    return repeated


def deduplicate_content(content: str, min_chunk_size: int = 10, min_occurrences: int = 3, 
                        silent_remove: bool = True) -> Tuple[str, Dict]:
    """
    Deduplicate content by removing repeated chunks.
    
    Args:
        content: The content to deduplicate
        min_chunk_size: Minimum chunk size in lines (default: 10)
        min_occurrences: Minimum occurrences to consider a chunk as duplicate (default: 3)
        silent_remove: If True, remove duplicates silently. If False, add comment markers.
    
    Returns:
        Tuple of (deduplicated_content, stats_dict)
    """
    lines = content.split('\n')
    repeated_chunks = find_repeated_chunks(content, min_chunk_size, min_occurrences)
    
    if not repeated_chunks:
        return content, {
            'removed_chunks': 0,
            'saved_lines': 0,
            'original_lines': len(lines),
            'final_lines': len(lines),
            'reduction_percent': 0.0,
            'duplicate_patterns': 0
        }
    
    # Track which lines to remove
    lines_to_remove = set()
    replacement_map = {}  # Maps (start, end) to replacement text
    
    # Process chunks by size (largest first) to avoid conflicts
    sorted_chunks = sorted(repeated_chunks.items(), 
                          key=lambda x: x[1]['count'] * len(x[1]['text']), 
                          reverse=True)
    
    stats = {
        'removed_chunks': 0,
        'saved_lines': 0,
        'original_lines': len(lines),
        'duplicate_patterns': len(repeated_chunks),
        'patterns_info': []
    }
    
    for chunk_hash, chunk_data in sorted_chunks:
        positions = chunk_data['positions']
        chunk_text = chunk_data['text']
        count = chunk_data['count']
        
        # Keep first occurrence, mark others for removal
        first_pos = positions[0]
        
        # Only process chunks that appear many times and are substantial
        if count < min_occurrences or len(chunk_text.strip()) < 100:
            continue
        
        # Mark all but first occurrence for removal
        removed_count = 0
        for start, end in positions[1:]:
            # Check if this range overlaps with already processed ranges
            overlap = False
            for existing_start, existing_end in replacement_map.keys():
                if not (end <= existing_start or start >= existing_end):
                    overlap = True
                    break
            
            if not overlap:
                # Mark lines for removal
                for line_num in range(start, end):
                    lines_to_remove.add(line_num)
                
                # Create replacement reference (or empty if silent)
                if silent_remove:
                    replacement_map[(start, end)] = None
                else:
                    replacement_map[(start, end)] = f"\n<!-- [DUPLICATE REMOVED: appears {count} times] -->\n"
                
                removed_count += 1
                stats['saved_lines'] += (end - start)
        
        if removed_count > 0:
            stats['removed_chunks'] += removed_count
            stats['patterns_info'].append({
                'count': count,
                'size': len(chunk_text),
                'preview': chunk_text[:100].replace('\n', ' ')
            })
    
    # Build deduplicated content
    deduplicated_lines = []
    i = 0
    while i < len(lines):
        if i in lines_to_remove:
            # Check if this is the start of a removed chunk
            replacement = None
            for (start, end), repl_text in replacement_map.items():
                if start == i:
                    replacement = repl_text
                    # Skip to end of chunk
                    i = end
                    break
            
            if replacement:
                deduplicated_lines.append(replacement)
            # If silent_remove and replacement is None, just skip the line
            elif not silent_remove:
                i += 1
            else:
                i += 1
        else:
            deduplicated_lines.append(lines[i])
            i += 1
    
    deduplicated_content = '\n'.join(deduplicated_lines)
    stats['final_lines'] = len(deduplicated_content.split('\n'))
    stats['reduction_percent'] = round((1 - stats['final_lines'] / stats['original_lines']) * 100, 2)
    
    return deduplicated_content, stats

