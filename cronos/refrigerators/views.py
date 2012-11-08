# -*- coding: utf-8 -*-

from cronos.refrigerators.forms import *
from cronos.refrigerators.tables import *
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

def refrigerators(request):
    sint_thermop = {'form1' : 0, 'form2' : 0, 'form3' : 0, 'form4' : 0, 'form5' : 0, 'form6' : 0, 'form7' : 0, 'form8' : 0}
    epif_pleuras = {'form1' : 0, 'form2' : 0, 'form3' : 0, 'form4' : 0, 'form5' : 0, 'form6' : 0, 'form7' : 0, 'form8' : 0}
    forms = {'form1' : 0, 'form2' : 0, 'form3' : 0, 'form4' : 0, 'form5' : 0, 'form6' : 0, 'form7' : 0, 'form8' : 0, 'form9' : 0, 'form10' : 0, 'form11' : 0, 'form12' : 0}
    results = {'form1' : 0, 'form2' : 0, 'form3' : 0, 'form4' : 0, 'form5' : 0, 'form6' : 0, 'form7' : 0, 'form8' : 0, 'form9' : 0, 'form10' : 0, 'form11' : 0, 'form12' : 0, 'total_result' : 0}
    tempdeltas = {'form1' : 0, 'form2' : 0, 'form3' : 0, 'form4' : 0, 'form5' : 0, 'form6' : 0, 'form8' : 0, 'form8_mt' : 0}

    temp_result = 0

    thermokrasia_aera_eisodou7 = 0
    thermokrasia_apothikeusis7 = 0
    ogkos_thalamou7 = 0
    thermokrasia_thalamou7 = 0
    enthalpia_aera_eisrois7 = 0
    ogkos_aera_eisrois7 = 0
    bathmos_psiksis8 = 0
    sint_bathmou_psiksis8 = 0
    eidiki_thermotita_pr8 = 0
    eidiki_thermotita_mt8 = 0
    ores_psiksis8 = 0
    maza8 = 0
    sint_kataps = 0
    lanthanousa_therm_ster8 = 0
    maza9 = 0
    timi_anapnois9 = 0
    diafora_fortia10 = 0
    sintelestis_asfaleias11 = 0
    sintelestis_diakop_leit12 = 0

    if request.method == 'POST':
        for i in range(1, 7, 1):
            text = '' + 'form' + str(i)
            forms[text] = Classes[0](request.POST)
        forms['form7'] = Classes[1](request.POST)
        forms['form8'] = Classes[2](request.POST)
        forms['form9'] = Classes[3](request.POST)
        forms['form10'] = Classes[4](request.POST)
        forms['form11'] = Classes[5](request.POST)
        forms['form12'] = Classes[6](request.POST)
        for i in 'form1', 'form2', 'form3', 'form4', 'form5', 'form6', 'form7', 'form8', 'form9', 'form10':
            if forms[i].is_valid():
                if str(type(forms[i])).find('FormA') > 0:
                    sint_thermop[i] = float(request.POST.get('sint_thermop'))
                    epif_pleuras[i] = float(request.POST.get('epif_pleuras'))
                    tempdeltas[i] = float(request.POST.get('dt'))
                    results[i] = sint_thermop[i] * epif_pleuras[i] * tempdeltas[i]
                if str(type(forms[i])).find('FormB') > 0:
                    thermokrasia_aera_eisodou7 = int(request.POST.get('thermokrasia_aera_eisodou7')) 
                    thermokrasia_apothikeusis7 = int(request.POST.get('thermokrasia_apothikeusis7')) 
                    ogkos_thalamou7 = int(request.POST.get('ogkos_thalamou7')) 
                    thermokrasia_thalamou7 = int(request.POST.get('thermokrasia_thalamou7'))
                    enthalpia_aera_eisrois7 = ENTHALPIA_AERA_EISROIS7[thermokrasia_apothikeusis7][thermokrasia_aera_eisodou7]
                    ogkos_aera_eisrois7 = OGKOS_AERA_EISROIS7[ogkos_thalamou7][thermokrasia_thalamou7]
                    results[i] = ogkos_aera_eisrois7 * enthalpia_aera_eisrois7
                if str(type(forms[i])).find('FormC') > 0:
                    ores_psiksis8 = float(request.POST.get('ores_psiksis8'))
                    maza8 = float(request.POST.get('maza8'))
                    tempdeltas[i] = float(request.POST.get('dt8'))
                    sint_kataps = int(request.POST.get('sint_kataps'))
                    if sint_kataps == 0:
                        sint_kataps = 'Συντήρηση'
                        bathmos_psiksis8 = request.POST.get('bathmos_psiksis8').split('::')[0]
                        sint_bathmou_psiksis8 = float(bathmos_psiksis8.split('-')[0])
                        eidiki_thermotita_pr8 = float(bathmos_psiksis8.split('-')[1])
                        print 'here'
                        results[i] = (maza8 * eidiki_thermotita_pr8 * tempdeltas[i]) / (ores_psiksis8 * 3600 * sint_bathmou_psiksis8)
                    else:
                        sint_kataps = 'Κατάψυξη'
                        bathmos_psiksis8 = request.POST.get('bathmos_psiksis8').split('::')[1]
                        eidiki_thermotita_pr8 = float(bathmos_psiksis8.split('-')[0])
                        eidiki_thermotita_mt8 = float(bathmos_psiksis8.split('-')[1])
                        lanthanousa_therm_ster8 = float(bathmos_psiksis8.split('-')[2])
                        tempdeltas['form8_mt'] = float(request.POST.get('dt_mt8'))
                        results[i] = ((maza8 * eidiki_thermotita_pr8 * tempdeltas[i]) + (maza8 * lanthanousa_therm_ster8) + (maza8 * eidiki_thermotita_mt8 * tempdeltas['form8_mt'])) / (ores_psiksis8 * 3600)
                if str(type(forms[i])).find('FormD') > 0:
                    maza9 = float(request.POST.get('maza9'))
                    timi_anapnois9 = float(request.POST.get('timi_anapnois9'))
                    results[i] = maza9 * timi_anapnois9
                if str(type(forms[i])).find('FormE') > 0:
                    diafora_fortia10 = float(request.POST.get('diafora_fortia10'))
                    results[i] = diafora_fortia10
        if forms['form11'].is_valid():
            sintelestis_asfaleias11 = float(request.POST.get('sintelestis_asfaleias11'))
            for k in range(1, 11, 1):
                text = '' + 'form' + str(k)
                temp_result = temp_result + results[text]
            results['form11'] = temp_result * sintelestis_asfaleias11
        if forms['form12'].is_valid():
            sintelestis_diakop_leit12 = float(request.POST.get('sintelestis_diakop_leit12'))
            results['form12'] = 24 * results['form11'] / sintelestis_diakop_leit12
        results['total_result'] = temp_result + results['form11'] + results['form12']
    else:
        for i in range(1, 7, 1):
            text = '' + 'form' + str(i)
            forms[text] = Classes[0](request.POST)
        forms['form7'] = Classes[1](request.POST)
        forms['form8'] = Classes[2](request.POST)
        forms['form9'] = Classes[3](request.POST)
        forms['form10'] = Classes[4](request.POST)
        forms['form11'] = Classes[5](request.POST)
        forms['form12'] = Classes[6](request.POST)
    return render_to_response('refrigerators.html', {
        'form1' : forms['form1'],
        'form2' : forms['form2'],
        'form3' : forms['form3'],
        'form4' : forms['form4'],
        'form5' : forms['form5'],
        'form6' : forms['form6'],
        'form7' : forms['form7'],
        'form8' : forms['form8'],
        'form9' : forms['form9'],
        'form10' : forms['form10'],
        'form11' : forms['form11'],
        'form12' : forms['form12'],
        'sint_thermop1' : sint_thermop['form1'],
        'sint_thermop2' : sint_thermop['form2'],
        'sint_thermop3' : sint_thermop['form3'],
        'sint_thermop4' : sint_thermop['form4'],
        'sint_thermop5' : sint_thermop['form5'],
        'sint_thermop6' : sint_thermop['form6'],
        'epif_pleuras1' : epif_pleuras['form1'],
        'epif_pleuras2' : epif_pleuras['form2'],
        'epif_pleuras3' : epif_pleuras['form3'],
        'epif_pleuras4' : epif_pleuras['form4'],
        'epif_pleuras5' : epif_pleuras['form5'],
        'epif_pleuras6' : epif_pleuras['form6'],
        'dt1' : tempdeltas['form1'],
        'dt2' : tempdeltas['form2'],
        'dt3' : tempdeltas['form3'],
        'dt4' : tempdeltas['form4'],
        'dt5' : tempdeltas['form5'],
        'dt6' : tempdeltas['form6'],
        'dt8' : tempdeltas['form8'],
        'dt_mt8' : tempdeltas['form8_mt'],
        'result1' : results['form1'],
        'result2' : results['form2'],
        'result3' : results['form3'],
        'result4' : results['form4'],
        'result5' : results['form5'],
        'result6' : results['form6'],
        'result7' : results['form7'],
        'result8' : results['form8'],
        'result9' : results['form9'],
        'result10' : results['form10'],
        'result11' : results['form11'],
        'result12' : results['form12'],
        'total_result' : results['total_result'],
        'enthalpia_aera_eisrois7' : enthalpia_aera_eisrois7,
        'ogkos_aera_eisrois7' : ogkos_aera_eisrois7,
        'bathmos_psiksis8' : bathmos_psiksis8,
        'sint_bathmou_psiksis8' : sint_bathmou_psiksis8,
        'eidiki_thermotita_pr8' : eidiki_thermotita_pr8,
        'eidiki_thermotita_mt8' : eidiki_thermotita_mt8,
        'ores_psiksis8' : ores_psiksis8,
        'maza8' : maza8,
        'sint_kataps' : sint_kataps,
        'lanthanousa_therm_ster8' : lanthanousa_therm_ster8,
        'maza9' : maza9,
        'timi_anapnois9' : timi_anapnois9,
        'diafora_fortia10' : diafora_fortia10,
        'sintelestis_asfaleias11' : sintelestis_asfaleias11,
        'sintelestis_diakop_leit12' : sintelestis_diakop_leit12,
        }, context_instance = RequestContext(request))
