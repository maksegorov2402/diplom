from django import forms


class BootstrapMixin:
    def _bootstrap_fields(self) -> None:
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(widget, forms.SelectMultiple):
                widget.attrs.setdefault("class", "form-select")
            elif isinstance(widget, (forms.Select, forms.DateInput, forms.DateTimeInput, forms.NumberInput, forms.TextInput, forms.EmailInput, forms.Textarea)):
                widget.attrs.setdefault("class", "form-control" if not isinstance(widget, forms.Select) else "form-select")


class BootstrapModelForm(BootstrapMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bootstrap_fields()


class BootstrapForm(BootstrapMixin, forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bootstrap_fields()
