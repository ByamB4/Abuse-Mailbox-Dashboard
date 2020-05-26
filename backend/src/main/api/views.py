from rest_framework.views import APIView
from rest_framework.response import Response
from pathlib import Path
from json import load

class MailListView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            f = open(str(Path(__file__).parent) + '/resources/general/full-data.json', 'r')
            data = load(f)
        except: 
            print('File not found')        
        return Response(data)

class MailChartView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            f = open(str(Path(__file__).parent) + '/resources/general/full-data.json', 'r')
            data = load(f)
        except: 
            print('File not found')
        ret = {
            'OUR_IPS_labels': list(data['OUR_IPS'].keys())[:15],
            'OUR_IPS_items': list(data['OUR_IPS'].values())[:15],
            'FROM_labels': [_[_.index('@')+1:] for _ in list(data['FROMS'].keys())][:10],
            'FROM_items': list(data['FROMS'].values())[:10],
            'CATEGORY_labels': list(data['CATEGORY'].keys()),
            'CATEGORY_items': list(data['CATEGORY'].values()),
            'DATE_labels': list(data['DATE'].keys()),
            'DATE_items': list(data['DATE'].values())
        }
        return Response(ret)