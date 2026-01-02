import json
from typing import Any, Callable, Optional


class mutable_proxy:
    def __init__(self, obj: Any, on_change: Callable):
        self._obj = obj
        self._on_change = on_change
        self._original_id = id(obj)

    def __getattr__(self, name):
        attr = getattr(self._obj, name)

        if callable(attr):
            return self._wrap_method(attr, name)
        elif self.is_mutable(attr):
            return mutable_proxy(obj=attr, on_change=self._on_change)
        return attr

    def _wrap_method(self, method, name):
        def wrapper(*args, **kwargs):
            result = method(*args, **kwargs)
            self._on_change()
            return result

        return wrapper

    def __getitem__(self, key):
        value = self._obj[key]

        if self.is_mutable(value):
            return mutable_proxy(obj=value, on_change=self._on_change)

        return value

    def __setitem__(self, key, value):
        self._obj[key] = value
        self._on_change()

    def __delitem__(self, key):
        del self._obj[key]
        self._on_change()

    def __repr__(self):
        return f"MutableProxy({repr(self._obj)})"

    def __str__(self):
        return str(self._obj)

    def __iter__(self):
        for item in self._obj:
            if self.is_mutable(item):
                yield mutable_proxy(obj=item, on_change=self._on_change)
            else:
                yield item

    def __contains__(self, key):
        return key in self._obj

    @staticmethod
    def is_mutable(obj):
        IMMUTABLE_TYPES = (
            int,
            float,
            complex,
            str,
            bytes,
            bool,
            type(None),
            type(...),
            tuple,
            frozenset,
            range,
        )
        if isinstance(obj, IMMUTABLE_TYPES):
            return False
        else:
            return True


class settings(mutable_proxy):
    def __init__(self, obj, auto_save_enabled=True, parent=None):
        super().__init__(obj, self.save)
        self.auto_save_enabled = auto_save_enabled
        self._parent = parent

    def get_or_create(self, key, default):
        if key in self:
            return self[key]
        else:
            self[key] = default
            return self[key]

    def save(self):
        if self.auto_save_enabled:
            if self._parent:
                self._parent.save()
            else:
                with open(self.file_path, "w") as f:
                    json.dump(self._obj, f)

    @staticmethod
    def from_file(file_path, auto_save_enabled=True):
        with open(file_path, "r") as f:
            obj = json.load(f)
            s = settings(obj, auto_save_enabled)
            s.file_path = file_path
            return s

    @staticmethod
    def from_settings(parent_settings, label, auto_save_enabled=True):
        return settings(
            obj=parent_settings.get_or_create(label,{}),
            auto_save_enabled=auto_save_enabled,
            parent=parent_settings,
        )
