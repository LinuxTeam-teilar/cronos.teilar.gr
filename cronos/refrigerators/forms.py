# -*- coding: utf-8 -*-

from cronos.refrigerators.tables import *
from django import forms

class Psigeia1Form(forms.Form):
    sint_thermop1 = forms.FloatField(label = "Συντελεστής Θερμοπερατότητας (K):", help_text = "KW/m^2*K")
    epif_pleuras1 = forms.FloatField(label = "Επιφάνεια Πλευράς:", help_text = "m^2")
    dt1 = forms.FloatField(label = "Διαφορά Θερμοκρασίας:", help_text = "K")

class Psigeia2Form(forms.Form):
    sint_thermop2 = forms.FloatField(label = "Συντελεστής Θερμοπερατότητας (K):", help_text = "KW/m^2*K")
    epif_pleuras2 = forms.FloatField(label = "Επιφάνεια Πλευράς:", help_text = "m^2")
    dt2 = forms.FloatField(label = "Διαφορά Θερμοκρασίας:", help_text = "K")

class Psigeia3Form(forms.Form):
    sint_thermop3 = forms.FloatField(label = "Συντελεστής Θερμοπερατότητας (K):", help_text = "KW/m^2*K")
    epif_pleuras3 = forms.FloatField(label = "Επιφάνεια Πλευράς:", help_text = "m^2")
    dt3 = forms.FloatField(label = "Διαφορά Θερμοκρασίας:", help_text = "K")

class Psigeia4Form(forms.Form):
    sint_thermop4 = forms.FloatField(label = "Συντελεστής Θερμοπερατότητας (K):", help_text = "KW/m^2*K")
    epif_pleuras4 = forms.FloatField(label = "Επιφάνεια Πλευράς:", help_text = "m^2")
    dt4 = forms.FloatField(label = "Διαφορά Θερμοκρασίας:", help_text = "K")

class Psigeia5Form(forms.Form):
    sint_thermop5 = forms.FloatField(label = "Συντελεστής Θερμοπερατότητας (K):", help_text = "KW/m^2*K")
    epif_pleuras5 = forms.FloatField(label = "Επιφάνεια Πλευράς:", help_text = "m^2")
    dt5 = forms.FloatField(label = "Διαφορά Θερμοκρασίας:", help_text = "K")

class Psigeia6Form(forms.Form):
    sint_thermop6 = forms.FloatField(label = "Συντελεστής Θερμοπερατότητας (K):", help_text = "KW/m^2*K")
    epif_pleuras6 = forms.FloatField(label = "Επιφάνεια Πλευράς:", help_text = "m^2")
    dt6 = forms.FloatField(label = "Διαφορά Θερμοκρασίας:", help_text = "K")

class Psigeia7Form(forms.Form):
    thermokrasia_apothikeusis7 = forms.ChoiceField(choices = THERMOKRASIA_APOTHIKEYSIS7, label = "Θερμοκρασία αποθήκευσης", help_text = "C")
    thermokrasia_aera_eisodou7 = forms.ChoiceField(choices = THERMOKRASIA_AERA_EISODOY7, label = "Θερμοκρασία - Σχετική υγρασία αέρα εισροής", help_text = "C")
    ogkos_thalamou7 = forms.ChoiceField(choices = OGKOS_THALAMOY7, label = "Όγκος Θαλάμου", help_text = "m^3")
    thermokrasia_thalamou7 = forms.ChoiceField(choices = THERMOKRASIA_THALAMOY7, label = "Θερμοκρασία Θαλάμου")

class Psigeia8Form(forms.Form):
    sint_kataps = forms.ChoiceField(choices = SINT_KATAPS, label = "Επιλογή αποθήκευσης:")
    bathmos_psiksis8 = forms.ChoiceField(choices = PROIONTA8, label = "Προϊόν:")
    dt8 = forms.FloatField(label = "Διαφορά Θερμοκρασίας συντήρησης:", help_text = "Κ")
    dt_mt8 = forms.FloatField(label = "Διαφορά θερμοκρασίας κατάψυξης:", help_text = "K", required = False)
    ores_psiksis8 = forms.FloatField(label = "Ώρες ψύξης:", help_text = "Ώρες")
    maza8 = forms.FloatField(label = "Μάζα:", help_text = "Kg")

class Psigeia9Form(forms.Form):
    maza9 = forms.FloatField(label = "Μάζα:", help_text = "Kg")
    timi_anapnois9 = forms.FloatField(label = "Τιμή αναπνοής:", help_text = "KW/Kg")

class Psigeia10Form(forms.Form):
    diafora_fortia10 = forms.FloatField(label = "Διάφορα φορτία:", help_text = "KWatt")

class Psigeia11Form(forms.Form):
    sintelestis_asfaleias11 = forms.FloatField(label = "Συντελεστής ασφαλείας:")

class Psigeia12Form(forms.Form):
    sintelestis_diakop_leit12 = forms.FloatField(label = "Συντελεστής διακοπτόμενης λειτουργίας:", help_text = "Ώρες")
