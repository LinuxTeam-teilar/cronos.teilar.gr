# -*- coding: utf-8 -*-

from cronos.refrigerators.tables import *
from django import forms

# ex Psugeia[1-6]Form
class FormA(forms.Form):
    sint_thermop = forms.FloatField(label = "Συντελεστής Θερμοπερατότητας (K):", help_text = "KW/m^2*K")
    epif_pleuras = forms.FloatField(label = "Επιφάνεια Πλευράς:", help_text = "m^2")
    dt = forms.FloatField(label = "Διαφορά Θερμοκρασίας:", help_text = "K")

# ex Psugeia7Form
class FormB(forms.Form):
    thermokrasia_apothikeusis7 = forms.ChoiceField(choices = THERMOKRASIA_APOTHIKEYSIS7, label = "Θερμοκρασία αποθήκευσης", help_text = "C")
    thermokrasia_aera_eisodou7 = forms.ChoiceField(choices = THERMOKRASIA_AERA_EISODOY7, label = "Θερμοκρασία - Σχετική υγρασία αέρα εισροής", help_text = "C")
    ogkos_thalamou7 = forms.ChoiceField(choices = OGKOS_THALAMOY7, label = "Όγκος Θαλάμου", help_text = "m^3")
    thermokrasia_thalamou7 = forms.ChoiceField(choices = THERMOKRASIA_THALAMOY7, label = "Θερμοκρασία Θαλάμου")

# ex Psugeia8Form
class FormC(forms.Form):
    sint_kataps = forms.ChoiceField(choices = SINT_KATAPS, label = "Επιλογή αποθήκευσης:")
    bathmos_psiksis8 = forms.ChoiceField(choices = PROIONTA8, label = "Προϊόν:")
    dt8 = forms.FloatField(label = "Διαφορά Θερμοκρασίας συντήρησης:", help_text = "Κ")
    dt_mt8 = forms.FloatField(label = "Διαφορά θερμοκρασίας κατάψυξης:", help_text = "K", required = False)
    ores_psiksis8 = forms.FloatField(label = "Ώρες ψύξης:", help_text = "Ώρες")
    maza8 = forms.FloatField(label = "Μάζα:", help_text = "Kg")

# ex Psugeia9Form
class FormD(forms.Form):
    maza9 = forms.FloatField(label = "Μάζα:", help_text = "Kg")
    timi_anapnois9 = forms.FloatField(label = "Τιμή αναπνοής:", help_text = "KW/Kg")

# ex Psugeia10Form
class FormE(forms.Form):
    diafora_fortia10 = forms.FloatField(label = "Διάφορα φορτία:", help_text = "KWatt")

# ex Psugeia11Form
class FormF(forms.Form):
    sintelestis_asfaleias11 = forms.FloatField(label = "Συντελεστής ασφαλείας:")

# ex Psugeia12Form
class FormG(forms.Form):
    sintelestis_diakop_leit12 = forms.FloatField(label = "Συντελεστής διακοπτόμενης λειτουργίας:", help_text = "Ώρες")
