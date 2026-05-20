from __future__ import annotations
from enum import Enum, auto


class ValueType(Enum):
    COLOR = auto()
    LENGTH = auto()
    NUMBER = auto()
    PERCENTAGE = auto()
    ANGLE = auto()
    TIME = auto()
    FREQUENCY = auto()
    RESOLUTION = auto()
    STRING = auto()
    URL = auto()
    IMAGE = auto()
    POSITION = auto()
    BOX = auto()
    SHAPE = auto()
    LINE_STYLE = auto()
    LINE_WIDTH = auto()
    FONT_NAME = auto()
    FONT_SIZE = auto()
    FONT_WEIGHT = auto()
    FONT_FAMILY = auto()
    TEXT_ALIGN = auto()
    TEXT_DECORATION = auto()
    TEXT_TRANSFORM = auto()
    DISPLAY = auto()
    POSITION_TYPE = auto()
    FLOAT_TYPE = auto()
    CLEAR_TYPE = auto()
    OVERFLOW = auto()
    VISIBILITY = auto()
    CURSOR = auto()
    LIST_STYLE = auto()
    BORDER_STYLE = auto()
    BORDER_COLLAPSE = auto()
    BACKGROUND_REPEAT = auto()
    BACKGROUND_ATTACHMENT = auto()
    BACKGROUND_CLIP = auto()
    BACKGROUND_ORIGIN = auto()
    BACKGROUND_SIZE = auto()
    FLEX_DIRECTION = auto()
    FLEX_WRAP = auto()
    JUSTIFY_CONTENT = auto()
    ALIGN_ITEMS = auto()
    ALIGN_SELF = auto()
    ALIGN_CONTENT = auto()
    GRID_TEMPLATE = auto()
    GRID_AUTO_FLOW = auto()
    TRANSFORM = auto()
    TRANSITION_TIMING = auto()
    ANIMATION_DIRECTION = auto()
    ANIMATION_FILL_MODE = auto()
    ANIMATION_PLAY_STATE = auto()
    BOX_SIZING = auto()
    VERTICAL_ALIGN = auto()
    WHITE_SPACE = auto()
    WORD_BREAK = auto()
    IDENT = auto()
    ANY = auto()


class PropertyDef:
    def __init__(
        self, name: str, allowed_types: list[ValueType],
        inherited: bool = False, supports_calc: bool = True,
    ) -> None:
        self.name = name
        self.allowed_types = allowed_types
        self.inherited = inherited
        self.supports_calc = supports_calc

    def __repr__(self) -> str:
        types = ", ".join(t.name for t in self.allowed_types)
        return f"PropertyDef({self.name}, [{types}])"


class CSSSpec:
    def __init__(self) -> None:
        self._properties: dict[str, PropertyDef] = {}
        self._load()

    def get(self, name: str) -> PropertyDef | None:
        return self._properties.get(name)

    @property
    def all_properties(self) -> dict[str, PropertyDef]:
        return dict(self._properties)

    def _add(self, name: str, *types: ValueType, **kwargs: bool) -> None:
        self._properties[name] = PropertyDef(name, list(types), **kwargs)

    def _load(self) -> None:
        COLOR = ValueType.COLOR
        LEN = ValueType.LENGTH
        NUM = ValueType.NUMBER
        PCT = ValueType.PERCENTAGE
        ANG = ValueType.ANGLE
        T = ValueType.TIME
        STR = ValueType.STRING
        ID = ValueType.IDENT
        ANY = ValueType.ANY

        # Layout & Display
        self._add("display", ValueType.DISPLAY, ID)
        self._add("position", ValueType.POSITION_TYPE, ID)
        self._add("top", LEN, PCT, ID)
        self._add("right", LEN, PCT, ID)
        self._add("bottom", LEN, PCT, ID)
        self._add("left", LEN, PCT, ID)
        self._add("float", ValueType.FLOAT_TYPE, ID)
        self._add("clear", ValueType.CLEAR_TYPE, ID)

        # Box model
        self._add("width", LEN, PCT, ID)
        self._add("min-width", LEN, PCT, ID)
        self._add("max-width", LEN, PCT, ID)
        self._add("height", LEN, PCT, ID)
        self._add("min-height", LEN, PCT, ID)
        self._add("max-height", LEN, PCT, ID)
        self._add("margin", LEN, PCT, ID)
        self._add("margin-top", LEN, PCT, ID)
        self._add("margin-right", LEN, PCT, ID)
        self._add("margin-bottom", LEN, PCT, ID)
        self._add("margin-left", LEN, PCT, ID)
        self._add("padding", LEN, PCT, ID)
        self._add("padding-top", LEN, PCT, ID)
        self._add("padding-right", LEN, PCT, ID)
        self._add("padding-bottom", LEN, PCT, ID)
        self._add("padding-left", LEN, PCT, ID)
        self._add("box-sizing", ValueType.BOX_SIZING, ID)

        # Border
        self._add("border", ValueType.LINE_WIDTH, ValueType.BORDER_STYLE, COLOR, ID)
        self._add("border-width", ValueType.LINE_WIDTH, ID)
        self._add("border-style", ValueType.BORDER_STYLE, ID)
        self._add("border-color", COLOR, ID)
        self._add("border-radius", LEN, PCT, ID)
        self._add("border-collapse", ValueType.BORDER_COLLAPSE, ID)

        self._add("border-top", ValueType.LINE_WIDTH, ValueType.BORDER_STYLE, COLOR, ID)
        self._add("border-right", ValueType.LINE_WIDTH, ValueType.BORDER_STYLE, COLOR, ID)
        self._add("border-bottom", ValueType.LINE_WIDTH, ValueType.BORDER_STYLE, COLOR, ID)
        self._add("border-left", ValueType.LINE_WIDTH, ValueType.BORDER_STYLE, COLOR, ID)
        self._add("border-top-width", ValueType.LINE_WIDTH, ID)
        self._add("border-right-width", ValueType.LINE_WIDTH, ID)
        self._add("border-bottom-width", ValueType.LINE_WIDTH, ID)
        self._add("border-left-width", ValueType.LINE_WIDTH, ID)
        self._add("border-top-style", ValueType.BORDER_STYLE, ID)
        self._add("border-right-style", ValueType.BORDER_STYLE, ID)
        self._add("border-bottom-style", ValueType.BORDER_STYLE, ID)
        self._add("border-left-style", ValueType.BORDER_STYLE, ID)
        self._add("border-top-color", COLOR, ID)
        self._add("border-right-color", COLOR, ID)
        self._add("border-bottom-color", COLOR, ID)
        self._add("border-left-color", COLOR, ID)
        self._add("border-top-left-radius", LEN, PCT, ID)
        self._add("border-top-right-radius", LEN, PCT, ID)
        self._add("border-bottom-left-radius", LEN, PCT, ID)
        self._add("border-bottom-right-radius", LEN, PCT, ID)

        # Outline
        self._add("outline", ValueType.LINE_WIDTH, ValueType.BORDER_STYLE, COLOR, ID)
        self._add("outline-width", ValueType.LINE_WIDTH, ID)
        self._add("outline-style", ValueType.BORDER_STYLE, ID)
        self._add("outline-color", COLOR, ID)
        self._add("outline-offset", LEN, ID)

        # Box shadow & filters
        self._add("box-shadow", LEN, COLOR, ID)

        # Background
        self._add("background", COLOR, ValueType.IMAGE, ValueType.POSITION,
                   ValueType.BACKGROUND_SIZE, ValueType.BACKGROUND_REPEAT,
                   ValueType.BACKGROUND_ATTACHMENT, ValueType.BACKGROUND_ORIGIN,
                   ValueType.BACKGROUND_CLIP, ID)
        self._add("background-color", COLOR, ID)
        self._add("background-image", ValueType.IMAGE, ValueType.URL, ID)
        self._add("background-position", ValueType.POSITION, LEN, PCT, ID)
        self._add("background-size", ValueType.BACKGROUND_SIZE, LEN, PCT, ID)
        self._add("background-repeat", ValueType.BACKGROUND_REPEAT, ID)
        self._add("background-attachment", ValueType.BACKGROUND_ATTACHMENT, ID)
        self._add("background-clip", ValueType.BACKGROUND_CLIP, ID)
        self._add("background-origin", ValueType.BACKGROUND_ORIGIN, ID)

        # Color
        self._add("color", COLOR, ID)
        self._add("opacity", NUM, ID)

        # Font
        self._add("font", ValueType.FONT_SIZE, ValueType.FONT_FAMILY,
                   ValueType.FONT_WEIGHT, ValueType.FONT_NAME, ID)
        self._add("font-family", ValueType.FONT_FAMILY, ID)
        self._add("font-size", ValueType.FONT_SIZE, LEN, PCT, ID)
        self._add("font-weight", ValueType.FONT_WEIGHT, NUM, ID)
        self._add("font-style", ID)
        self._add("font-variant", ID)
        self._add("line-height", NUM, LEN, PCT, ID)

        # Text
        self._add("text-align", ValueType.TEXT_ALIGN, ID)
        self._add("text-decoration", ValueType.TEXT_DECORATION, COLOR, ID)
        self._add("text-transform", ValueType.TEXT_TRANSFORM, ID)
        self._add("text-indent", LEN, PCT, ID)
        self._add("text-shadow", LEN, COLOR, ID)
        self._add("text-overflow", ID)
        self._add("vertical-align", ValueType.VERTICAL_ALIGN, LEN, PCT, ID)
        self._add("white-space", ValueType.WHITE_SPACE, ID)
        self._add("word-break", ValueType.WORD_BREAK, ID)
        self._add("word-spacing", LEN, ID)
        self._add("letter-spacing", LEN, ID)

        # Flex
        self._add("flex", NUM, LEN, PCT, ID)
        self._add("flex-grow", NUM, ID)
        self._add("flex-shrink", NUM, ID)
        self._add("flex-basis", LEN, PCT, ID)
        self._add("flex-direction", ValueType.FLEX_DIRECTION, ID)
        self._add("flex-wrap", ValueType.FLEX_WRAP, ID)
        self._add("justify-content", ValueType.JUSTIFY_CONTENT, ID)
        self._add("align-items", ValueType.ALIGN_ITEMS, ID)
        self._add("align-self", ValueType.ALIGN_SELF, ID)
        self._add("align-content", ValueType.ALIGN_CONTENT, ID)
        self._add("gap", LEN, PCT, ID)
        self._add("row-gap", LEN, PCT, ID)
        self._add("column-gap", LEN, PCT, ID)

        # Grid
        self._add("grid", ValueType.GRID_TEMPLATE, ID)
        self._add("grid-template", ValueType.GRID_TEMPLATE, ID)
        self._add("grid-template-columns", ValueType.GRID_TEMPLATE, LEN, PCT, ID)
        self._add("grid-template-rows", ValueType.GRID_TEMPLATE, LEN, PCT, ID)
        self._add("grid-template-areas", STR, ID)
        self._add("grid-column", ID, NUM)
        self._add("grid-row", ID, NUM)
        self._add("grid-auto-flow", ValueType.GRID_AUTO_FLOW, ID)
        self._add("grid-auto-columns", LEN, PCT, ID)
        self._add("grid-auto-rows", LEN, PCT, ID)
        self._add("grid-column-start", ID, NUM)
        self._add("grid-column-end", ID, NUM)
        self._add("grid-row-start", ID, NUM)
        self._add("grid-row-end", ID, NUM)
        self._add("place-items", ValueType.ALIGN_ITEMS, ValueType.JUSTIFY_CONTENT, ID)
        self._add("place-content", ValueType.ALIGN_CONTENT, ValueType.JUSTIFY_CONTENT, ID)
        self._add("place-self", ValueType.ALIGN_SELF, ValueType.JUSTIFY_CONTENT, ID)

        # Overflow & Visibility
        self._add("overflow", ValueType.OVERFLOW, ID)
        self._add("overflow-x", ValueType.OVERFLOW, ID)
        self._add("overflow-y", ValueType.OVERFLOW, ID)
        self._add("visibility", ValueType.VISIBILITY, ID)
        self._add("z-index", NUM, ID)

        # Transform & Transition & Animation
        self._add("transform", ValueType.TRANSFORM, ID)
        self._add("transform-origin", LEN, PCT, ID)
        self._add("transition", ValueType.TRANSITION_TIMING, T, ID)
        self._add("transition-property", ID)
        self._add("transition-duration", T, ID)
        self._add("transition-timing-function", ValueType.TRANSITION_TIMING, ID)
        self._add("transition-delay", T, ID)
        self._add("animation", T, ValueType.TRANSITION_TIMING, T, NUM,
                   ValueType.ANIMATION_DIRECTION, ValueType.ANIMATION_FILL_MODE,
                   ValueType.ANIMATION_PLAY_STATE, ID)
        self._add("animation-name", ID)
        self._add("animation-duration", T, ID)
        self._add("animation-timing-function", ValueType.TRANSITION_TIMING, ID)
        self._add("animation-delay", T, ID)
        self._add("animation-iteration-count", NUM, ID)
        self._add("animation-direction", ValueType.ANIMATION_DIRECTION, ID)
        self._add("animation-fill-mode", ValueType.ANIMATION_FILL_MODE, ID)
        self._add("animation-play-state", ValueType.ANIMATION_PLAY_STATE, ID)

        # List
        self._add("list-style", ValueType.LIST_STYLE, ID)
        self._add("list-style-type", ID)
        self._add("list-style-position", ID)
        self._add("list-style-image", ValueType.IMAGE, ValueType.URL, ID)

        # Table
        self._add("table-layout", ID)
        self._add("caption-side", ID)
        self._add("empty-cells", ID)

        # Content
        self._add("content", STR, ID)
        self._add("counter-increment", ID, NUM)
        self._add("counter-reset", ID, NUM)

        # Cursor
        self._add("cursor", ValueType.CURSOR, ValueType.URL, ID)

        # Other
        self._add("clip", ValueType.SHAPE, ID)
        self._add("clip-path", ValueType.SHAPE, ValueType.URL, ID)
        self._add("filter", ID, ValueType.URL)
        self._add("backdrop-filter", ID, ValueType.URL)
        self._add("pointer-events", ID)
        self._add("user-select", ID)
        self._add("resize", ID)
        self._add("scroll-behavior", ID)
        self._add("object-fit", ID)
        self._add("object-position", ValueType.POSITION, LEN, PCT, ID)
        self._add("order", NUM, ID)
        self._add("isolation", ID)
        self._add("mix-blend-mode", ID)

        # Logical properties
        self._add("inset", LEN, PCT, ID)
        self._add("inset-block", LEN, PCT, ID)
        self._add("inset-inline", LEN, PCT, ID)
        self._add("inset-block-start", LEN, PCT, ID)
        self._add("inset-block-end", LEN, PCT, ID)
        self._add("inset-inline-start", LEN, PCT, ID)
        self._add("inset-inline-end", LEN, PCT, ID)
        self._add("margin-block", LEN, PCT, ID)
        self._add("margin-inline", LEN, PCT, ID)
        self._add("margin-block-start", LEN, PCT, ID)
        self._add("margin-block-end", LEN, PCT, ID)
        self._add("margin-inline-start", LEN, PCT, ID)
        self._add("margin-inline-end", LEN, PCT, ID)
        self._add("padding-block", LEN, PCT, ID)
        self._add("padding-inline", LEN, PCT, ID)
        self._add("padding-block-start", LEN, PCT, ID)
        self._add("padding-block-end", LEN, PCT, ID)
        self._add("padding-inline-start", LEN, PCT, ID)
        self._add("padding-inline-end", LEN, PCT, ID)
        self._add("border-block", ValueType.LINE_WIDTH, ValueType.BORDER_STYLE, COLOR, ID)
        self._add("border-inline", ValueType.LINE_WIDTH, ValueType.BORDER_STYLE, COLOR, ID)
        self._add("border-block-width", ValueType.LINE_WIDTH, ID)
        self._add("border-inline-width", ValueType.LINE_WIDTH, ID)
        self._add("border-block-style", ValueType.BORDER_STYLE, ID)
        self._add("border-inline-style", ValueType.BORDER_STYLE, ID)
        self._add("border-block-color", COLOR, ID)
        self._add("border-inline-color", COLOR, ID)

        # Modern CSS
        self._add("aspect-ratio", NUM, ID)
        self._add("accent-color", COLOR, ID)
        self._add("caret-color", COLOR, ID)
        self._add("color-scheme", ID)
        self._add("scroll-margin", LEN, ID)
        self._add("scroll-margin-top", LEN, ID)
        self._add("scroll-margin-right", LEN, ID)
        self._add("scroll-margin-bottom", LEN, ID)
        self._add("scroll-margin-left", LEN, ID)
        self._add("scroll-padding", LEN, PCT, ID)
        self._add("scroll-padding-top", LEN, PCT, ID)
        self._add("scroll-padding-right", LEN, PCT, ID)
        self._add("scroll-padding-bottom", LEN, PCT, ID)
        self._add("scroll-padding-left", LEN, PCT, ID)
        self._add("scrollbar-width", ID)
        self._add("scrollbar-color", COLOR, ID)
        self._add("text-underline-offset", LEN, ID)
        self._add("text-decoration-thickness", LEN, ID)
        self._add("text-decoration-color", COLOR, ID)
        self._add("text-decoration-style", ID)
        self._add("translate", LEN, PCT, ID)
        self._add("rotate", ANG, ID)
        self._add("scale", NUM, ID)
        self._add("container", ID)
        self._add("container-type", ID)
        self._add("container-name", ID)
        self._add("will-change", ID)

        # CSS Variables (custom properties)
        # Any value allowed for --* properties

    def is_custom_property(self, name: str) -> bool:
        return name.startswith("--")

    def validate_value(self, prop_name: str, value_type: ValueType, value_str: str) -> str | None:
        """Returns an error message if invalid, None if valid."""
        prop = self.get(prop_name)
        if prop is None:
            if self.is_custom_property(prop_name):
                return None
            return f"Unknown CSS property: {prop_name}"

        if value_type == ValueType.ANY or ValueType.ANY in prop.allowed_types:
            return None

        if value_type in prop.allowed_types:
            return None

        if value_type == ValueType.IDENT:
            return None

        if value_type == ValueType.LENGTH and ValueType.LINE_WIDTH in prop.allowed_types:
            return None

        if value_type == ValueType.LINE_WIDTH and ValueType.LENGTH in prop.allowed_types:
            return None

        if value_type == ValueType.NUMBER:
            len_like = {ValueType.LENGTH, ValueType.LINE_WIDTH, ValueType.PERCENTAGE, ValueType.FONT_SIZE}
            if len_like & set(prop.allowed_types):
                return None

        allowed = ", ".join(t.name for t in prop.allowed_types)
        return f"Type mismatch for '{prop_name}': expected [{allowed}], got {value_type.name}"
