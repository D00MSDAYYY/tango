import streamlit as st
from enum import Enum





class ToolbarBuilder:
    """Builder для создания тулбаров"""

    def __init__(self):
        self._buttons: List[ToolbarButton] = []

    def add_button(
        self,
        name: str,
        callback: Callable,
        size: ButtonSize = ButtonSize.MEDIUM,
        icon: Optional[str] = None,
        tooltip: Optional[str] = None,
        disabled: bool = False,
    ) -> "ToolbarBuilder":
        """Добавить кнопку"""
        self._buttons.append(
            ToolbarButton(name, size, callback, icon, tooltip, disabled)
        )
        return self

    def build(self) -> "DynamicToolbar":
        """Построить тулбар"""
        return DynamicToolbar(self._buttons)


class DynamicToolbar:
    """Динамический тулбар, построенный через Builder"""

    def __init__(self, buttons: List[ToolbarButton]):
        self.buttons = buttons

    def render(self, container=None) -> None:
        """Отрендерить тулбар"""
        if not self.buttons:
            return

        # Создаем колонки
        columns = (
            st.columns(spec=[btn.size.value for btn in self.buttons], gap="small")
            if container is None
            else container.columns(spec=[btn.size.value for btn in self.buttons])
        )

        # Рендерим кнопки
        for col, btn in zip(columns, self.buttons):
            with col:
                if btn.disabled:
                    st.button(
                        btn.display_name,
                        disabled=True,
                        help=btn.tooltip,
                        use_container_width=True,
                    )
                else:
                    with st.popover(
                        btn.display_name, use_container_width=True, help=btn.tooltip
                    ):
                        btn.callback()
