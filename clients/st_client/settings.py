import json



def is_mutable(obj):
    IMMUTABLE_TYPES = (
        int, float, complex, str, bytes, bool, 
        type(None), type(...), tuple, frozenset, range
    )
    if isinstance(obj, IMMUTABLE_TYPES):
        return False
    else:
        return True
    
class mutable_object():
    def __init__(self, auto_save=True):
        pass

class settings(mutable_object):
    def __init__(self, file_path=None, auto_save=True):
        pass
    

class settings:
    def __init__(self, file_path=None, auto_save=True):
        if file_path:
            with open(file_path, "r") as f:
                self._data = json.load(f)

        self.file_path = file_path
        self.auto_save = auto_save
        self._parent = None

    def __getitem__(self, key):
        return self._data[key]

    def __delitem__(self, key):
        del self._data[key]
        if self.auto_save:
            self.save()

    def get(self, key, default=None):
        return self._data.get(key, default)

    def get_or_create(self, key, default):
        if key in self._data:
            return self._data[key]
        else:
            self._data[key] = default
            if self.auto_save:
                self.save()
            return default

    def __setitem__(self, key, value):
        self._data[key] = value

        if self.auto_save:
            self.save()

    def __iter__(self):
        return iter(self._data)

    def extract_settings(self, label, auto_save=True):
        extracted_settings = settings(auto_save=auto_save)
        _data = self[label]

        from collections.abc import MutableMapping

        if all(isinstance(_data, requirement) for requirement in [MutableMapping]):
            extracted_settings._data = _data
        else:
            raise TypeError(
                f"Ожидается объект, совместимый со словарем (MutableMapping), "
                f"получен {type(_data).__name__}"
            )

        extracted_settings._parent = self
        return extracted_settings

    def extract_or_create_settings(self, label, default_data=None, auto_save=True):
        if label in self:
            return self.extract_settings(label, auto_save)
        else:
            default_data = default_data or {}
            self[label] = default_data.copy()
            return self.extract_settings(label, auto_save)

    def save(self):
        if self._parent:
            self._parent.save()
        else:
            with open(self.file_path, "w") as f:
                json.dump(self._data, f)
