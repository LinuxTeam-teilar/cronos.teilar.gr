# -*- coding: utf-8 -*-

from cronos.refrigeratos.forms import *
from cronos.refrigeratos.tables import *
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

def refrigeratos(request):
    sint_thermop1 = None
    epif_pleuras1 = None
    dt1 = None
    result1 = None
    sint_thermop2 = None
    epif_pleuras2 = None
    dt2 = None
    result2 = None
    sint_thermop3 = None
    epif_pleuras3 = None
    dt3 = None
    result3 = None
    sint_thermop4 = None
    epif_pleuras4 = None
    dt4 = None
    result4 = None
    sint_thermop5 = None
    epif_pleuras5 = None
    dt5 = None
    result5 = None
    sint_thermop6 = None
    epif_pleuras6 = None
    dt6 = None
    result6 = None
    thermokrasia_aera_eisodou7 = None
    thermokrasia_apothikeusis7 = None
    ogkos_thalamou7 = None
    thermokrasia_thalamou7 = None
    enthalpia_aera_eisrois7 = None
    ogkos_aera_eisrois7 = None
    result7 = None
    bathmos_psiksis8 = None
    sint_bathmou_psiksis8 = None
    eidiki_thermotita_pr8 = None
    eidiki_thermotita_mt8 = None
    dt8 = None
    dt_mt8 = None
    ores_psiksis8 = None
    maza8 = None
    sint_kataps = None
    lanthanousa_therm_ster8 = None
    result8 = None
    maza9 = None
    timi_anapnois9 = None
    result9 = None
    diafora_fortia10 = None
    result10 = None
    sintelestis_asfaleias11 = None
    result11 = None
    sintelestis_diakop_leit12 = None
    result12 = None
    total_result = None
    if request.method == 'POST':
        form1 = Psigeia1Form(request.POST)
        form2 = Psigeia2Form(request.POST)
        form3 = Psigeia3Form(request.POST)
        form4 = Psigeia4Form(request.POST)
        form5 = Psigeia5Form(request.POST)
        form6 = Psigeia6Form(request.POST)
        form7 = Psigeia7Form(request.POST)
        form8 = Psigeia8Form(request.POST)
        form9 = Psigeia9Form(request.POST)
        form10 = Psigeia10Form(request.POST)
        form11 = Psigeia11Form(request.POST)
        form12 = Psigeia12Form(request.POST)
        if form1.is_valid():
            sint_thermop1 = float(request.POST.get('sint_thermop1'))
            epif_pleuras1 = float(request.POST.get('epif_pleuras1'))
            dt1 = float(request.POST.get('dt1'))
            result1 = sint_thermop1 * epif_pleuras1 * dt1
        if form2.is_valid():
            sint_thermop2 = float(request.POST.get('sint_thermop2'))
            epif_pleuras2 = float(request.POST.get('epif_pleuras2'))
            dt2 = float(request.POST.get('dt2'))
            result2 = sint_thermop2 * epif_pleuras2 * dt2
        if form3.is_valid():
            sint_thermop3 = float(request.POST.get('sint_thermop3'))
            epif_pleuras3 = float(request.POST.get('epif_pleuras3'))
            dt3 = float(request.POST.get('dt3'))
            result3 = sint_thermop3 * epif_pleuras3 * dt3
        if form4.is_valid():
            sint_thermop4 = float(request.POST.get('sint_thermop4'))
            epif_pleuras4 = float(request.POST.get('epif_pleuras4'))
            dt4 = float(request.POST.get('dt4'))
            result4 = sint_thermop4 * epif_pleuras4 * dt4
        if form5.is_valid():
            sint_thermop5 = float(request.POST.get('sint_thermop5'))
            epif_pleuras5 = float(request.POST.get('epif_pleuras5'))
            dt5 = float(request.POST.get('dt5'))
            result5 = sint_thermop5 * epif_pleuras5 * dt5
        if form6.is_valid():
            sint_thermop6 = float(request.POST.get('sint_thermop6'))
            epif_pleuras6 = float(request.POST.get('epif_pleuras6'))
            dt6 = float(request.POST.get('dt6'))
            result6 = sint_thermop6 * epif_pleuras6 * dt6
        if form7.is_valid():
            thermokrasia_aera_eisodou7 = int(request.POST.get('thermokrasia_aera_eisodou7'))
            thermokrasia_apothikeusis7 = int(request.POST.get('thermokrasia_apothikeusis7'))
            ogkos_thalamou7 = int(request.POST.get('ogkos_thalamou7'))
            thermokrasia_thalamou7 = int(request.POST.get('thermokrasia_thalamou7'))
            enthalpia_aera_eisrois7 = ENTHALPIA_AERA_EISROIS7[thermokrasia_apothikeusis7][thermokrasia_aera_eisodou7]
            ogkos_aera_eisrois7 = OGKOS_AERA_EISROIS7[ogkos_thalamou7][thermokrasia_thalamou7]
            result7 = ogkos_aera_eisrois7 * enthalpia_aera_eisrois7
        if form8.is_valid():
            ores_psiksis8 = float(request.POST.get('ores_psiksis8'))
            maza8 = float(request.POST.get('maza8'))
            dt8 = float(request.POST.get('dt8'))
            sint_kataps = int(request.POST.get('sint_kataps'))
            if sint_kataps == 0:
                sint_kataps = 'Συντήρηση'
                bathmos_psiksis8 = request.POST.get('bathmos_psiksis8').split('::')[0]
                sint_bathmou_psiksis8 = float(bathmos_psiksis8.split('-')[0])
                eidiki_thermotita_pr8 = float(bathmos_psiksis8.split('-')[1])
                print 'here'
                result8 = (maza8 * eidiki_thermotita_pr8 * dt8) / (ores_psiksis8 * 3600 * sint_bathmou_psiksis8)
            else:
                sint_kataps = 'Κατάψυξη'
                bathmos_psiksis8 = request.POST.get('bathmos_psiksis8').split('::')[1]
                eidiki_thermotita_pr8 = float(bathmos_psiksis8.split('-')[0])
                eidiki_thermotita_mt8 = float(bathmos_psiksis8.split('-')[1])
                lanthanousa_therm_ster8 = float(bathmos_psiksis8.split('-')[2])
                dt_mt8 = float(request.POST.get('dt_mt8'))
                result8 = ((maza8 * eidiki_thermotita_pr8 * dt8) + (maza8 * lanthanousa_therm_ster8) + (maza8 * eidiki_thermotita_mt8 * dt_mt8)) / (ores_psiksis8 * 3600)
        if form9.is_valid():
            maza9 = float(request.POST.get('maza9'))
            timi_anapnois9 = float(request.POST.get('timi_anapnois9'))
            result9 = maza9 * timi_anapnois9
        if form10.is_valid():
            diafora_fortia10 = float(request.POST.get('diafora_fortia10'))
            result10 = diafora_fortia10
        total_result = result1 + result2 +result3 + result4 + result5 + result6 + result7 + result8 + result9 + result10
        if form11.is_valid():
            sintelestis_asfaleias11 = float(request.POST.get('sintelestis_asfaleias11'))
            result11 = total_result * sintelestis_asfaleias11
        if form12.is_valid():
            sintelestis_diakop_leit12 = float(request.POST.get('sintelestis_diakop_leit12'))
            result12 = 24 * result11 / sintelestis_diakop_leit12
        total_result = total_result + result11 + result12
    else:
        form1 = Psigeia1Form(request.POST)
        form2 = Psigeia2Form(request.POST)
        form3 = Psigeia3Form(request.POST)
        form4 = Psigeia4Form(request.POST)
        form5 = Psigeia5Form(request.POST)
        form6 = Psigeia6Form(request.POST)
        form7 = Psigeia7Form(request.POST)
        form8 = Psigeia8Form(request.POST)
        form9 = Psigeia9Form(request.POST)
        form10 = Psigeia10Form(request.POST)
        form11 = Psigeia11Form(request.POST)
        form12 = Psigeia12Form(request.POST)
    return render_to_response('refrigeratos.html', {
        'form1': form1,
        'sint_thermop1': sint_thermop1,
        'epif_pleuras1': epif_pleuras1,
        'dt1': dt1,
        'result1': result1,
        'form2': form2,
        'sint_thermop2': sint_thermop2,
        'epif_pleuras2': epif_pleuras2,
        'dt2': dt2,
        'result2': result2,
        'form3': form3,
        'sint_thermop3': sint_thermop3,
        'epif_pleuras3': epif_pleuras3,
        'dt3': dt3,
        'result3': result3,
        'form4': form4,
        'sint_thermop4': sint_thermop4,
        'epif_pleuras4': epif_pleuras4,
        'dt4': dt4,
        'result4': result4,
        'form5': form5,
        'sint_thermop5': sint_thermop5,
        'epif_pleuras5': epif_pleuras5,
        'dt5': dt5,
        'result5': result5,
        'form6': form6,
        'sint_thermop6': sint_thermop6,
        'epif_pleuras6': epif_pleuras6,
        'dt6': dt6,
        'result6': result6,
        'form7': form7,
        'enthalpia_aera_eisrois7': enthalpia_aera_eisrois7,
        'ogkos_aera_eisrois7': ogkos_aera_eisrois7,
        'result7': result7,
        'form8': form8,
        'bathmos_psiksis8': bathmos_psiksis8,
        'sint_bathmou_psiksis8': sint_bathmou_psiksis8,
        'eidiki_thermotita_pr8': eidiki_thermotita_pr8,
        'eidiki_thermotita_mt8': eidiki_thermotita_mt8,
        'dt8': dt8,
        'dt_mt8': dt_mt8,
        'ores_psiksis8': ores_psiksis8,
        'maza8': maza8,
        'sint_kataps': sint_kataps,
        'lanthanousa_therm_ster8': lanthanousa_therm_ster8,
        'result8': result8,
        'form9': form9,
        'maza9': maza9,
        'timi_anapnois9': timi_anapnois9,
        'result9': result9,
        'form10': form10,
        'diafora_fortia10': diafora_fortia10,
        'result10': result10,
        'form11': form11,
        'sintelestis_asfaleias11': sintelestis_asfaleias11,
        'result11': result11,
        'form12': form12,
        'sintelestis_diakop_leit12': sintelestis_diakop_leit12,
        'result12': result12,
        'total_result': total_result,
        }, context_instance = RequestContext(request))
