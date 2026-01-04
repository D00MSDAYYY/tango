from typing import Callable, Literal, Optional, final
from dataclasses import dataclass, field
import streamlit as st


@dataclass
@final
class button:
    label: str = field()

    key: Optional[str | int] = field(default=None)
    help: Optional[str] = field(default=None)
    on_click: Optional[Callable] = field(default=None)
    args: Optional[list | tuple] = field(default=None)
    kwargs: Optional[dict] = field(default=None)
    type: Literal["primary", "secondary", "tertiary"] = field(default="secondary")
    icon: Optional[str] = field(default=None)
    disabled: bool = field(default=False)
    width: Literal["content", "stretch"] | int = field(default="content")
    fraction: int = field(default=1)
    shortcut: Optional[str] = field(default=None)

    def show(self):
        st.button(
            label=self.label,
            key=self.key,
            help=self.help,
            on_click=self.on_click,
            args=self.args,
            kwargs=self.kwargs,
            type=self.type,
            icon=self.icon,
            disabled=self.disabled,
            width=self.width,
            shortcut=self.shortcut,
        )

