# -*- coding: utf-8 -*-

from cronos.refrigerators.forms import *
from cronos.refrigerators.tables import *
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

def refrigerators(request):
    forms = {'form1' : 0, 'form2' : 0, 'form3' : 0, 'form4' : 0, 'form5' : 0, 'form6' : 0, 'form7' : 0, 'form8' : 0, 'form9' : 0, 'form10' : 0, 'form11' : 0, 'form12' : 0}
    results = {'form1' : 0, 'form2' : 0, 'form3' : 0, 'form4' : 0, 'form5' : 0, 'form6' : 0, 'form7' : 0, 'form8' : 0, 'form9' : 0, 'form10' : 0, 'form11' : 0, 'form12' : 0, 'total_result' : 0}

    temp_result = 0
    enthalpia_aera_eisrois7 = 0
    ogkos_aera_eisrois7 = 0
    sint_bathmou_psiksis8 = 0
    eidiki_thermotita_pr8 = 0
    eidiki_thermotita_mt8 = 0
    lanthanousa_therm_ster8 = 0
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
                    forms[i]['sint_thermop'] = float(request.POST.get('sint_thermop'))
                    forms[i]['epif_pleuras'] = float(request.POST.get('epif_pleuras'))
                    forms[i]['dt']  = float(request.POST.get('dt'))
                    results[i] = sint_thermop[i] * epif_pleuras[i] * tempdeltas[i]
                if str(type(forms[i])).find('FormB') > 0:
                    forms[i]['thermokrasia_aera_eisodou7'] = int(request.POST.get('thermokrasia_aera_eisodou7')) 
                    forms[i]['thermokrasia_apothikeusis7'] = int(request.POST.get('thermokrasia_apothikeusis7')) 
                    forms[i]['ogkos_thalamou7'] = int(request.POST.get('ogkos_thalamou7')) 
                    forms[i]['thermokrasia_thalamou7'] = int(request.POST.get('thermokrasia_thalamou7'))
                    enthalpia_aera_eisrois7 = ENTHALPIA_AERA_EISROIS7[forms[i]['thermokrasia_apothikeusis7']][forms[i]['thermokrasia_aera_eisodou7']]
                    ogkos_aera_eisrois7 = OGKOS_AERA_EISROIS7[forms[i]['ogkos_thalamou7']][forms[i]['thermokrasia_thalamou7']]
                    results[i] = ogkos_aera_eisrois7 * enthalpia_aera_eisrois7
                if str(type(forms[i])).find('FormC') > 0:
                    forms[i]['ores_psiksis8'] = float(request.POST.get('ores_psiksis8'))
                    forms[i]['maza8'] = float(request.POST.get('maza8'))
                    forms[i]['dt'] = float(request.POST.get('dt8'))
                    forms[i]['sint_kataps'] = int(request.POST.get('sint_kataps'))
                    if forms[i]['sint_kataps'] == 0:
                        forms[i]['sint_kataps'] = 'Συντήρηση'
                        forms[i]['bathmos_psiksis8'] = request.POST.get('bathmos_psiksis8').split('::')[0]
                        sint_bathmou_psiksis8 = float(forms[i]['bathmos_psiksis8'].split('-')[0])
                        eidiki_thermotita_pr8 = float(forms[i]['bathmos_psiksis8'].split('-')[1])
                        print 'here'
                        results[i] = (forms[i]['maza8'] * eidiki_thermotita_pr8 * forms[i]['dt8']) / (forms[i]['ores_psiksis8'] * 3600 * sint_bathmou_psiksis8)
                    else:
                        forms[i]['sint_kataps'] = 'Κατάψυξη'
                        forms[i]['bathmos_psiksis8'] = request.POST.get('bathmos_psiksis8').split('::')[1]
                        eidiki_thermotita_pr8 = float(forms[i]['bathmos_psiksis8'].split('-')[0])
                        eidiki_thermotita_mt8 = float(forms[i]['bathmos_psiksis8'].split('-')[1])
                        lanthanousa_therm_ster8 = float(forms[i]['bathmos_psiksis8'].split('-')[2])
                        forms[i]['dt_mt'] = float(request.POST.get('dt_mt'))
                        results[i] = ((forms[i]['maza8'] * eidiki_thermotita_pr8 * forms[i]['dt']) + (forms[i]['maza8'] * lanthanousa_therm_ster8) + (forms[i]['maza8'] * eidiki_thermotita_mt8 * forms[i]['dt_mt'])) / (forms[i]['ores_psiksis8'] * 3600)
                if str(type(forms[i])).find('FormD') > 0:
                    forms[i]['maza9'] = float(request.POST.get('maza9'))
                    forms[i]['timi_anapnois9'] = float(request.POST.get('timi_anapnois9'))
                    results[i] = forms[i]['maza9'] * forms[i]['timi_anapnois9']
                if str(type(forms[i])).find('FormE') > 0:
                    forms[i]['diafora_fortia10'] = float(request.POST.get('diafora_fortia10'))
                    results[i] = forms[i]['diafora_fortia10']
        if forms['form11'].is_valid():
            forms[i]['sintelestis_asfaleias11'] = float(request.POST.get('sintelestis_asfaleias11'))
            for k in range(1, 11, 1):
                text = '' + 'form' + str(k)
                temp_result = temp_result + results[text]
            results['form11'] = temp_result * forms['sintelestis_asfaleias11']
        if forms['form12'].is_valid():
            forms[i]['sintelestis_diakop_leit12'] = float(request.POST.get('sintelestis_diakop_leit12'))
            results['form12'] = 24 * results['form11'] / forms[i]['sintelestis_diakop_leit12']
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
        'sint_thermop1' : forms['form1']['sint_thermop'],
        'sint_thermop2' : forms['form2']['sint_thermop'],
        'sint_thermop3' : forms['form3']['sint_thermop'],
        'sint_thermop4' : forms['form4']['sint_thermop'],
        'sint_thermop5' : forms['form5']['sint_thermop'],
        'sint_thermop6' : forms['form6']['sint_thermop'],
        'epif_pleuras1' : forms['form1']['epif_pleuras'],
        'epif_pleuras2' : forms['form2']['epif_pleuras'],
        'epif_pleuras3' : forms['form3']['epif_pleuras'],
        'epif_pleuras4' : forms['form4']['epif_pleuras'],
        'epif_pleuras5' : forms['form5']['epif_pleuras'],
        'epif_pleuras6' : forms['form6']['epif_pleuras'],
        'dt1' : forms['form1']['dt'],
        'dt2' : forms['form2']['dt'],
        'dt3' : forms['form3']['dt'],
        'dt4' : forms['form4']['dt'],
        'dt5' : forms['form5']['dt'],
        'dt6' : forms['form6']['dt'],
        'dt8' : forms['form8']['dt'],
        'dt_mt8' : forms['form8']['dt_mt'],
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
        'bathmos_psiksis8' : forms['form8']['bathmos_psiksis8'],
        'sint_bathmou_psiksis8' : sint_bathmou_psiksis8,
        'eidiki_thermotita_pr8' : eidiki_thermotita_pr8,
        'eidiki_thermotita_mt8' : eidiki_thermotita_mt8,
        'ores_psiksis8' : forms['form8']['ores_psiksis8'],
        'maza8' : forms['form8']['maza8'],
        'sint_kataps' : forms['form8']['sint_kataps'],
        'lanthanousa_therm_ster8' : lanthanousa_therm_ster8,
        'maza9' : forms['form9']['maza9'],
        'timi_anapnois9' : forms['form9']['timi_anapnois9'],
        'diafora_fortia10' : forms['form10']['diafora_fortia10'],
        'sintelestis_asfaleias11' : forms['form11']['sintelestis_asfaleias11'],
        'sintelestis_diakop_leit12' : forms['form12']['sintelestis_diakop_leit12'],
        }, context_instance = RequestContext(request))
