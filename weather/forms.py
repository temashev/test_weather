from django import forms


class CitySearchForm(forms.Form):
    city_name = forms.CharField(label='Город', max_length=100, widget=forms.TextInput(attrs={'autocomplete': 'off'}))
