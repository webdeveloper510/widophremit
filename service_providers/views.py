from Remit_Assure.package import *
from Remit_Assure.helpers import error_logs

################################ Blogs Views ################################

class Blogs_list_view(APIView):
    def post(self, request):
        try:
            data = list(Blogs.objects.all().values())  
            return JsonResponse({'code': 200, 'message': 'success', 'data': data})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_content = str(e) + " in line " + str(exc_tb.tb_lineno) + " in Blogs_list_view"
            error_logs(file_content)
            return JsonResponse({'code': 500, 'message': "Internal server error"}, status=500)
