from typing import Callable, Literal, Optional, final
from dataclasses import dataclass, field
import streamlit as st

@dataclass
@final
class popover:
    label: str = field()

    help: Optional[str] = field(default=None)
    on_click: Optional[Callable] = field(default=None)
    type: Literal["primary", "secondary", "tertiary"] = field(default="secondary")
    icon: Optional[str] = field(default=None)
    disabled: bool = field(default=False)
    width: Literal["content", "stretch"] | int = field(default="content")
    fraction: int = field(default=1)

    def show(self):
        with st.popover(
            label=self.label,
            help=self.help,
            type=self.type,
            icon=self.icon,
            disabled=self.disabled,
            width=self.width,
        ):
            self.on_click()
