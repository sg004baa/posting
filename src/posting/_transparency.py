"""Keep the terminal's default colours intact throughout Textual's renderer.

Posting paints every background with the terminal's own default colour
(``ansi_default``). Textual mostly passes that straight through, but when a
Rich style is converted back into a Textual style (e.g. widgets which render
Rich ``Text``, such as the footer keys), ``Color.from_rich_color`` resolves
``default`` colours into opaque RGB values taken from ``ansi_theme`` — which
paints cells that should have stayed transparent.

Importing this module patches the conversion so that Rich's ``default``
colour survives as ``ansi_default``.
"""

from rich.color import Color as RichColor, ColorType
from textual.color import Color

_ANSI_DEFAULT = Color(0, 0, 0, ansi=-1)

_original_from_rich_color = Color.from_rich_color.__func__


def _from_rich_color(cls, rich_color: RichColor | None, theme=None) -> Color:
    if rich_color is not None and rich_color.type == ColorType.DEFAULT:
        return _ANSI_DEFAULT
    return _original_from_rich_color(cls, rich_color, theme)


def apply() -> None:
    """Install the colour-preserving patch (idempotent)."""
    if Color.from_rich_color.__func__ is not _from_rich_color:
        Color.from_rich_color = classmethod(_from_rich_color)
