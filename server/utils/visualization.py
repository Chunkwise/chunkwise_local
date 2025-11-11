"""Class for visualizing chunks"""

# Adapted from:
# Minhas, Bhavnick AND Nigam, Shreyash (2025)
# "Chonkie: A no-nonsense fast, lightweight, and efficient text chunking library"
# https://github.com/chonkie-inc/chonkie/blob/55edbad3457043573ed576c6be7e60ff64525a29/src/chonkie/__init__.py

import html
import warnings
from server_types import Chunk

# light themes
LIGHT_THEMES = {
    # Pastel colored rainbow theme
    "pastel": [
        "#FFADAD",
        "#FFD6A5",
        "#FDFFB6",
        "#CAFFBF",
        "#9BF6FF",
        "#A0C4FF",
        "#BDB2FF",
        "#FFC6FF",
    ],
    # Tiktokenizer theme: [ “#bae6fc”, “#fde68a”, “#bbf7d0”, “#fed7aa”, “#a5f3fc”, “#e5e7eb”, “#eee2fd”, “#e4f9c0”, “#fecdd3”]
    "tiktokenizer": [
        "#bae6fc",
        "#fde68a",
        "#bbf7d0",
        "#fed7aa",
        "#a5f3fc",
        "#e5e7eb",
        "#eee2fd",
        "#e4f9c0",
        "#fecdd3",
    ],
    # New example light theme
    "ocean_breeze": [
        "#E0FFFF",  # Light Cyan
        "#B0E0E6",  # Powder Blue
        "#ADD8E6",  # Light Blue
        "#87CEEB",  # Sky Blue
        "#4682B4",  # Steel Blue
    ],
}

# dark themes
DARK_THEMES = {
    # Tiktokenizer but with darker colors
    "tiktokenizer_dark": [
        "#2A4E66",
        "#80662A",
        "#2A6648",
        "#66422A",
        "#2A4A66",
        "#3A3D40",
        "#55386E",
        "#3A6640",
        "#66353B",
    ],
    # Pastel but with darker colors
    "pastel_dark": [
        "#5C2E2E",
        "#5C492E",
        "#4F5C2E",
        "#2E5C4F",
        "#2E3F5C",
        "#3A3A3A",
        "#4F2E5C",
        "#2E5C3F",
    ],
    # New example dark theme
    "midnight": [
        "#00008B",  # DarkBlue
        "#483D8B",  # DarkSlateBlue
        "#2F4F4F",  # DarkSlateGray
        "#191970",  # MidnightBlue
    ],
}

# light mode color
TEXT_COLOR_LIGHT = "#333333"
# dark mode color
TEXT_COLOR_DARK = "#FFFFFF"

MAIN_TEMPLATE = """
<div class="content-box">
    <div class="text-display">{html_parts}</div>
</div>
"""


class Visualizer:
    """Visualizer class for Chonkie.

    Attributes:
        theme (str): The theme to use for the visualizer (default is "pastel")

    Methods:
        get_html

    """

    def __init__(self, theme: str | list[str] = "pastel") -> None:
        """Initialize the Visualizer.

        Args:
            theme: The theme to use for the visualizer (default is PASTEL_THEME)

        """

        # We want the editor's text color to apply by default for custom themes
        # If the theme is a string, get the theme
        if isinstance(theme, str):
            self.theme, self.text_color = self._get_theme(theme)
            self.theme_name = theme
        else:
            self.text_color = ""
            self.theme = theme
            self.theme_name = "custom"

    # NOTE: This is a helper function to manage the theme
    def _get_theme(self, theme: str) -> tuple[list[str], str]:
        """Get the theme from the theme name."""
        if theme in DARK_THEMES:
            return DARK_THEMES[theme], TEXT_COLOR_DARK
        elif theme in LIGHT_THEMES:
            return LIGHT_THEMES[theme], TEXT_COLOR_LIGHT
        else:
            raise ValueError(f"Invalid theme: {theme}")

    def _get_color(self, index: int) -> str:
        """Cycles through the appropriate color list."""
        return self.theme[index % len(self.theme)]

    def _reconstruct_text_from_chunks(self, chunks: list[Chunk]) -> str:
        """Reconstruct the full text from a list of chunks, handling overlaps."""
        # Sort chunks by start_index to handle overlaps correctly
        sorted_chunks = sorted(chunks, key=lambda x: x.start_index)

        # Check if chunks have the required attributes
        for chunk in sorted_chunks:
            if (
                not hasattr(chunk, "text")
                or not hasattr(chunk, "start_index")
                or not hasattr(chunk, "end_index")
            ):
                raise AttributeError(
                    "Chunks must have 'text', 'start_index', and 'end_index' attributes for automatic text reconstruction."
                )

        # Reconstruct full text by merging chunks
        reconstructed_text = ""
        last_end = 0

        for chunk in sorted_chunks:
            start_idx = chunk.start_index

            if start_idx >= last_end:
                # No overlap, append chunk text directly
                reconstructed_text += chunk.text
                last_end = len(reconstructed_text)  # fix for overlapped chunks
            else:
                # Handle overlap by taking only the non-overlapping part
                overlap_offset = last_end - start_idx
                if overlap_offset < len(chunk.text):
                    reconstructed_text += chunk.text[overlap_offset:]
                    last_end = len(reconstructed_text)  # fix for overlapped chunks

        return reconstructed_text

    # NOTE: This is a helper function to manage overlapping chunk visualizations
    def _darken_color(self, hex_color: str, amount: float = 0.7) -> str:
        """Darkens a hex color by a multiplier (0 to 1)."""
        try:
            hex_color = hex_color.lstrip("#")
            if len(hex_color) != 6:
                if len(hex_color) == 3:
                    hex_color = "".join([c * 2 for c in hex_color])
                else:
                    raise ValueError("Invalid hex color format")
            rgb = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
            darker_rgb = tuple(max(0, int(c * amount)) for c in rgb)
            return "#{:02x}{:02x}{:02x}".format(*darker_rgb)
        except Exception as e:
            print(f"Warning: Could not darken color {hex_color}: {e}")
            return "#808080"

    def get_html(
        self,
        chunks: list[Chunk],
        full_text: str | None = None,
    ) -> str:
        """
        Returns HTML visualization of chunks as a string

        Args:
            chunks: A list of chunk objects with 'start_index' and 'end_index'.
            full_text: The complete original text. If None, it attempts reconstruction.
            title (str): The title for the browser tab.

        """
        # (Input validation and text reconstruction logic remains the same)
        if not chunks:
            print("No chunks to visualize.")
            raise AttributeError("No chunks to visualize")
        # If the full text is not provided, we'll try to reconstruct it (assuming the chunks are reconstructable)
        if full_text is None:
            try:
                full_text = self._reconstruct_text_from_chunks(chunks)
            except AttributeError:
                raise AttributeError(
                    "Error: Chunks must have 'text', 'start_index', and 'end_index' attributes for automatic text reconstruction."
                )
            except Exception as e:
                raise ValueError(f"Error reconstructing full text: {e}.")

        # --- 1. Validate Spans and Prepare Data ---
        validated_spans = []
        text_length = len(full_text)
        for i, chunk in enumerate(chunks):
            try:
                start, end = int(chunk.start_index), int(chunk.end_index)
                start = max(0, start)
                end = max(0, end)
                if start < end and start < text_length:
                    effective_end = min(end, text_length)
                    token_count = chunk.token_count
                    validated_spans.append(
                        {
                            "id": i,
                            "start": start,
                            "end": effective_end,
                            "tokens": token_count,
                        }
                    )
            except (AttributeError, TypeError, ValueError):
                warnings.warn(
                    f"Warning: Skipping chunk with invalid start/end index: {chunk}"
                )
                continue

        # --- 2. Generate HTML Parts (Event-based with Overlap Detection) ---
        html_parts = []
        last_processed_idx = 0
        events = []

        # Create events for each span
        for span_data in validated_spans:
            events.append((span_data["start"], 1, span_data["id"]))
            events.append((span_data["end"], -1, span_data["id"]))
        events.sort()

        # Initialize the active chunk IDs set
        active_chunk_ids: set[int] = set()

        # Iterate through the events
        for i in range(len(events)):
            event_idx, event_type, chunk_id = events[i]
            num_active = len(active_chunk_ids)
            current_bg_color = "transparent"
            # If there are active chunks, determine the primary chunk and its color
            hover_title = ""
            if num_active > 0:
                min_active_chunk_id = min(active_chunk_ids)
                primary_chunk_data = next(
                    (s for s in validated_spans if s["id"] == min_active_chunk_id), None
                )
                if primary_chunk_data:
                    base_color = self._get_color(primary_chunk_data["id"])
                    current_bg_color = (
                        base_color
                        if num_active == 1
                        else self._darken_color(base_color, 0.65)
                    )
                    token_count = primary_chunk_data["tokens"]
                    hover_title = f"Chunk {primary_chunk_data['id']} | Start: {primary_chunk_data['start']} | End: {primary_chunk_data['end']} | Tokens: {token_count if token_count else 'Token count not provided by chunker'}{' (Overlap)' if num_active > 1 else ''}"
            # Get the text segment to process
            text_segment = full_text[last_processed_idx:event_idx]

            # If there is text to process, escape it and add it to the HTML parts
            if text_segment:
                escaped_segment = html.escape(text_segment).replace("\n", "<br>")
                # If there is a background color, add the title attribute and the span tags
                if current_bg_color != "transparent":
                    title_attr = (
                        f' title="{html.escape(hover_title)}"' if hover_title else ""
                    )
                    html_parts.append(
                        f'<span style="background-color: {current_bg_color};"{title_attr}>'
                    )
                    html_parts.append(escaped_segment)
                    html_parts.append("</span>")
                else:
                    html_parts.append(escaped_segment)
            last_processed_idx = event_idx
            if event_type == 1:
                active_chunk_ids.add(chunk_id)
            elif event_type == -1:
                active_chunk_ids.discard(chunk_id)
        # Process final segment
        if last_processed_idx < text_length:
            text_segment = full_text[last_processed_idx:]
            escaped_segment = html.escape(text_segment).replace("\n", "<br>")
            num_active = len(active_chunk_ids)
            current_bg_color = "transparent"
            hover_title = ""
            if num_active > 0:
                min_active_chunk_id = min(active_chunk_ids)
                primary_chunk_data = next(
                    (s for s in validated_spans if s["id"] == min_active_chunk_id), None
                )
                if primary_chunk_data:
                    base_color = self._get_color(primary_chunk_data["id"])
                    current_bg_color = (
                        base_color
                        if num_active == 1
                        else self._darken_color(base_color, 0.65)
                    )
                    hover_title = f"Chunk {primary_chunk_data['id']} | Start: {primary_chunk_data['start']} | End: {primary_chunk_data['end']} | Tokens: {primary_chunk_data['tokens']}{' (Overlap)' if num_active > 1 else ''}"
            if current_bg_color != "transparent":
                title_attr = (
                    f' title="{html.escape(hover_title)}"' if hover_title else ""
                )
                html_parts.append(
                    f'<span style="background-color: {current_bg_color};"{title_attr}>'
                )
                html_parts.append(escaped_segment)
                html_parts.append("</span>")
            else:
                html_parts.append(escaped_segment)

        # --- 3. Assemble the final HTML ---

        # Main Content (remain the same)
        main_content = MAIN_TEMPLATE.format(html_parts="".join(html_parts))

        # --- 4. Return HTML ---
        return main_content

    def __repr__(self) -> str:
        """Return the string representation of the Visualizer."""
        return f"Visualizer(theme={self.theme})"
