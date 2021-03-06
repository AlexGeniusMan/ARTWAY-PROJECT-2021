import random
import string
from datetime import timedelta
from django.utils.datetime_safe import datetime
from rest_framework import status
from rest_framework.response import Response
from django.views.generic.base import View
from rest_framework.views import APIView
from django.http import HttpResponse
from project.settings import DOMAIN_NAME
from .permissions import *
from .serializers import *
import os
from .models import User
from django.contrib.auth.models import Group
import segno
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas
from svglib.svglib import svg2rlg
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase import ttfonts


class PrintCurrentArtifactsView(APIView):
    """
    Shows PDF file for printing
    """
    permission_classes = (IsMuseumAdmin,)

    def get_new_filename(self):
        letters_and_digits = string.ascii_letters + string.digits
        result_str = ''.join((random.choice(letters_and_digits) for i in range(60)))
        return result_str

    def scale(self, drawing, scaling_factor):
        """
        Scale a reportlab.graphics.shapes.Drawing()
        object while maintaining the aspect ratio
        """
        scaling_x = scaling_factor
        scaling_y = scaling_factor

        drawing.width = drawing.minWidth() * scaling_x
        drawing.height = drawing.height * scaling_y
        drawing.scale(scaling_x, scaling_y)
        return drawing

    def get_new_pdf(self, request, list_of_artifacts):
        print_type = request.data['print_type']

        MyFontObject = ttfonts.TTFont('Arial', 'arial.ttf')
        pdfmetrics.registerFont(MyFontObject)
        fname = self.get_new_filename()
        pdf_name = f'./media/prints/{fname}.pdf'
        my_canvas = canvas.Canvas(pdf_name)
        my_canvas.setFont('Arial', 12)

        number_of_artifacts = len(list_of_artifacts)
        if print_type == 'tiny':
            i = 0
            skip = 0
            while number_of_artifacts > 0:
                drawing = svg2rlg('mirea_emblem_black.svg')
                scaling_factor = 0.1
                emblem = self.scale(drawing, scaling_factor=scaling_factor)

                qr = segno.make(f'https://{DOMAIN_NAME}/artifacts/{list_of_artifacts[i + skip * 9].id}', micro=False)
                qr.save('qr.svg')
                drawing = svg2rlg('qr.svg')
                scaling_factor = 3.5
                qr_code = self.scale(drawing, scaling_factor=scaling_factor)

                if i % 2 == 0:
                    k = 0
                    j = 0
                else:
                    k = 278
                    j = 1
                renderPDF.draw(emblem, my_canvas, 180 + k, 70 + (i - j) * 80)
                my_canvas.drawString(48 + k, 165 + (i - j) * 80, f'{list_of_artifacts[i + skip * 9].name}')
                renderPDF.draw(qr_code, my_canvas, 35 + k, 39 + (i - j) * 80)
                my_canvas.drawString(160 + k, 53 + (i - j) * 80, f'ID: {list_of_artifacts[i + skip * 9].id}')
                my_canvas.rect(30 + k, 34 + (i - j) * 80, 257, 150)
                number_of_artifacts -= 1
                if i < 9:
                    i += 1
                else:
                    i = 0
                    skip += 1
                    my_canvas.setFont('Arial', 10)
                    my_canvas.drawString(467, 15, 'Powered by Dev.gang')
                    my_canvas.showPage()
                    my_canvas.setFont('Arial', 12)
                    my_canvas.rect(0, 0, 595, 842)
        elif print_type == 'medium':
            i = 0
            skip = 0
            while number_of_artifacts > 0:
                drawing = svg2rlg('mirea_emblem_black.svg')
                scaling_factor = 0.1
                emblem = self.scale(drawing, scaling_factor=scaling_factor)

                qr = segno.make(f'https://{DOMAIN_NAME}/artifacts/{list_of_artifacts[i + skip * 4].id}', micro=False)
                qr.save('qr.svg')
                drawing = svg2rlg('qr.svg')
                scaling_factor = 7
                qr_code = self.scale(drawing, scaling_factor=scaling_factor)

                if i % 2 == 0:
                    k = 0
                    j = 0
                else:
                    k = 278
                    j = 1
                renderPDF.draw(emblem, my_canvas, 115 + k, 315 + (i - j) * 202)
                my_canvas.drawString(55 + k, 300 + (i - j) * 202, f'{list_of_artifacts[i + skip * 4].name}')
                my_canvas.drawString(55 + k, 280 + (i - j) * 202, f'ID: {list_of_artifacts[i + skip * 4].id}')
                renderPDF.draw(qr_code, my_canvas, 28 + k, 35 + (i - j) * 202)
                my_canvas.rect(30 + k, 32 + (i - j) * 202, 257, 375)
                number_of_artifacts -= 1
                if i < 3:
                    i += 1
                else:
                    i = 0
                    skip += 1
                    my_canvas.setFont('Arial', 10)
                    my_canvas.drawString(467, 15, 'Powered by Dev.gang')
                    my_canvas.showPage()
                    my_canvas.setFont('Arial', 12)
                    my_canvas.rect(0, 0, 595, 842)
        elif print_type == 'large':
            i = 0
            while number_of_artifacts > 0:
                drawing = svg2rlg('mirea_emblem_black.svg')
                scaling_factor = 0.25
                emblem = self.scale(drawing, scaling_factor=scaling_factor)

                qr = segno.make(f'https://{DOMAIN_NAME}/artifacts/{list_of_artifacts[i].id}', micro=False)
                qr.save('qr.svg')
                drawing = svg2rlg('qr.svg')
                scaling_factor = 15
                qr_code = self.scale(drawing, scaling_factor=scaling_factor)

                my_canvas.setFont('Arial', 16)
                renderPDF.draw(emblem, my_canvas, 200, 600)
                my_canvas.drawString(82, 560, f'{list_of_artifacts[i].name}')
                my_canvas.drawString(82, 530, f'ID: {list_of_artifacts[i].id}')
                renderPDF.draw(qr_code, my_canvas, 25, 10)

                number_of_artifacts -= 1
                i += 1
                my_canvas.showPage()
                my_canvas.setFont('Arial', 16)

        my_canvas.save()
        pdf_name = f'http://{DOMAIN_NAME}/media/prints/{fname}.pdf'
        return pdf_name

    def post(self, request):
        artifacts_pk = request.data['artifacts']
        list_of_artifacts = list()
        for artifact_pk in artifacts_pk:
            artifact = Artifact.objects.get(pk=artifact_pk)
            list_of_artifacts.append(artifact)
        pdf_name = self.get_new_pdf(request, list_of_artifacts)
        return Response(pdf_name)


class IsUserExistsView(APIView):
    """
    Shows whether a user exists with the current email
    """

    def post(self, request):
        email = request.data['email']
        try:
            user = User.objects.get(email=email)
            return Response({"status": status.HTTP_200_OK})
        except:
            return Response({"status": status.HTTP_404_NOT_FOUND})


class UserStatusesView(APIView):
    """
    Shows user statuses
    """

    def get(self, request):
        if request.user.is_authenticated:
            return Response({
                'is_service_super_admin': request.user.groups.filter(name='service_super_admins').exists(),
                'is_museum_super_admin': request.user.groups.filter(name='museum_super_admins').exists(),
                'is_museum_admin': request.user.groups.filter(name='museum_admins').exists(),
                'is_museum_cashier': request.user.groups.filter(name='museum_cashiers').exists(),
            })
        else:
            return Response({
                'is_service_super_admin': False,
                'is_museum_super_admin': False,
                'is_museum_admin': False,
                'is_museum_cashier': False,
            })


class AllTicketsView(APIView):
    """
    Shows all active tickets, creates new ticket
    """
    permission_classes = (IsMuseumCashier,)

    def get_new_token(self):
        letters_and_digits = string.ascii_letters + string.digits
        result_str = ''.join((random.choice(letters_and_digits) for i in range(30)))
        return result_str

    def scale(self, drawing, scaling_factor):
        """
        Scale a reportlab.graphics.shapes.Drawing()
        object while maintaining the aspect ratio
        """
        scaling_x = scaling_factor
        scaling_y = scaling_factor

        drawing.width = drawing.minWidth() * scaling_x
        drawing.height = drawing.height * scaling_y
        drawing.scale(scaling_x, scaling_y)
        return drawing

    def get_new_pdf(self, request, ticket_id, token):
        qr = segno.make(f'http://{DOMAIN_NAME}/?token={token}', micro=False)
        qr.save('qr.svg')
        MyFontObject = ttfonts.TTFont('Arial', 'arial.ttf')
        pdfmetrics.registerFont(MyFontObject)
        pdf_name = f'./media/tickets/ticket_{ticket_id}.pdf'
        my_canvas = canvas.Canvas(pdf_name)

        drawing = svg2rlg('mirea_emblem_black.svg')
        scaling_factor = 0.15
        scaled_drawing = self.scale(drawing, scaling_factor=scaling_factor)
        renderPDF.draw(scaled_drawing, my_canvas, 450, 680)

        my_canvas.setFont('Arial', 18)
        my_canvas.drawString(50, 730, f'{request.user.museum}')

        my_canvas.setFont('Arial', 14)
        strings = (
            '',
            'Инструкция:',
            '• Перейдите к сканированию QR-кода выбранного экспоната или введите его ID',
            '• На странице экспоната Вы сможете получить информацию о нём,',
            '  а также прослушать аудиогид',
            '• Любите искусство вместе с ArtWay',
            '',
            '',
            'Ваш персональный QR-код для перехода на страницу сервиса:',
        )
        i = 650
        for new_string in strings:
            my_canvas.drawString(50, i, new_string)
            i -= 20

        drawing = svg2rlg('qr.svg')
        scaling_factor = 10
        scaled_drawing = self.scale(drawing, scaling_factor=scaling_factor)
        renderPDF.draw(scaled_drawing, my_canvas, 95, 70)

        my_canvas.setFont('Arial', 10)
        my_canvas.drawString(470, 20, 'Powered by Dev.gang')
        my_canvas.save()
        pdf_name = f'tickets/ticket_{ticket_id}.pdf'
        return pdf_name

    def get_tickets(self, request):
        d = datetime.now() - timedelta(hours=request.user.museum.ticket_lifetime)
        tickets = Ticket.objects.filter(museum=request.user.museum).filter(created_at__gte=d).order_by('-created_at')
        tickets_data = list()
        for el in tickets:
            hour = el.created_at.hour + 3
            if hour >= 24:
                hour = hour - 24
            ticket = {
                'id': el.id,
                'token': el.token,
                'pdf': f'https://{DOMAIN_NAME}/media/{el.pdf.name}',
                'date_year': el.created_at.year,
                'date_month': el.created_at.month,
                'date_day': el.created_at.day,
                'date_hour': hour,
                'date_minute': el.created_at.minute,
                'date_second': el.created_at.second,
            }
            tickets_data.append(ticket)
        return tickets_data

    def get(self, request):
        return Response(self.get_tickets(request))

    def post(self, request):
        try:
            token = self.get_new_token()
            ticket = Ticket(token=token, museum=request.user.museum)
            ticket.save()
            pdf_name = self.get_new_pdf(request, ticket.id, token)
            ticket.pdf = pdf_name
            ticket.save()
            return Response(self.get_tickets(request))
        except Exception:
            return Response(Exception)


class RelocateArtifactView(APIView):
    """
    Relocates current artifact to another hall of current museum
    """
    permission_classes = (IsMuseumAdmin,)

    def post(self, request):
        cur = Artifact.objects.get(pk=request.data['artifact_pk'])
        hall_pk = cur.hall.id

        # deleting obj from old hall
        if cur.prev != None:
            up = Artifact.objects.get(pk=cur.prev)
            try:
                down = Artifact.objects.get(prev=cur.id)
                down.prev = up.id
            except:
                pass
        else:
            try:
                down = Artifact.objects.get(prev=cur.id)
                down.prev = None
            except:
                pass

        cur.prev = None

        # adding obj to new hall
        cur.hall = Hall.objects.get(pk=request.data['hall_pk'])

        temp_len = len(Artifact.objects.filter(hall=cur.hall))
        if temp_len > 1:
            artifact = Artifact.objects.filter(hall=cur.hall).get(prev=None)
            for i in range(len(Artifact.objects.filter(hall=cur.hall)) - 1):
                artifact = Artifact.objects.get(prev=artifact.id)
            cur.prev = artifact.id
        elif temp_len == 1:
            artifact = Artifact.objects.get(hall=cur.hall)
            if artifact.id != cur.id:
                cur.prev = artifact.id
            else:
                cur.prev = None
        else:
            cur.prev = None

        cur.save()
        try:
            up.save()
        except:
            pass
        try:
            down.save()
        except:
            pass
        return Response(serialize_hall_and_artifacts(request, hall_pk))


class SwapArtifactsView(APIView):
    """
    Swaps current artifact with upper or lower artifact
    """
    permission_classes = (IsMuseumAdmin,)

    def swap_and_save_artifact(self, swap_type, request):
        if swap_type == 'up':
            cur = Artifact.objects.get(pk=request.data['obj_id'])
        elif swap_type == 'down':
            cur = Artifact.objects.get(prev=request.data['obj_id'])
        up = Artifact.objects.get(pk=cur.prev)
        try:
            down = Artifact.objects.get(prev=cur.id)
            cur.prev = None  # deleting obj from list
            down.prev = up.id
            cur.prev = up.prev  # adding obj to list
            up.prev = cur.id
            cur.save()
            up.save()
            down.save()
        except:  # exception only if 'cur' is the last el in the list (then obj 'down' doesn't exists)
            if swap_type == 'down':
                cur = Artifact.objects.get(prev=request.data['obj_id'])
                up = Artifact.objects.get(pk=request.data['obj_id'])
            cur.prev = up.prev
            up.prev = cur.id
            cur.save()
            up.save()
        return True

    def post(self, request):
        swap_type = request.data['swap_type']
        self.swap_and_save_artifact(swap_type, request)
        hall_pk = Artifact.objects.get(pk=request.data['obj_id']).hall.id
        location_pk = Hall.objects.get(pk=hall_pk).location.id
        return Response(serialize_hall_and_artifacts(request, hall_pk))


class CurrentArtifactView(APIView):
    """
    Shows current artifact
    """
    permission_classes = (IsMuseumAdmin,)

    def get_artifact(self, request, location_pk, hall_pk, artifact_pk):
        artifact = Artifact.objects.get(pk=artifact_pk)
        serializer = ArtifactSerializer(artifact, context={'request': request})
        return serializer.data

    def delete_artifact(self, request, location_pk, hall_pk, artifact_pk):
        cur = Artifact.objects.get(pk=artifact_pk)
        try:
            down = Artifact.objects.get(prev=cur.id)
            down.prev = cur.prev
            down.save()
        except:
            pass
        cur.delete()
        return True

    def get(self, request, location_pk, hall_pk, artifact_pk):
        return Response(self.get_artifact(request, location_pk, hall_pk, artifact_pk))

    def put(self, request, location_pk, hall_pk, artifact_pk):
        artifact = Artifact.objects.get(pk=artifact_pk)

        artifact.name = request.data['name']
        artifact.description = request.data['description']
        try:
            if request.data['img_1'] == 'null':
                artifact.img_1 = None
            else:
                artifact.img_1 = request.FILES['img_1']
        except:
            pass
        try:
            if request.data['img_2'] == 'null':
                artifact.img_2 = None
            else:
                artifact.img_2 = request.FILES['img_2']
        except:
            pass
        try:
            if request.data['img_3'] == 'null':
                artifact.img_3 = None
            else:
                artifact.img_3 = request.FILES['img_3']
        except:
            pass
        try:
            if request.data['img_4'] == 'null':
                artifact.img_4 = None
            else:
                artifact.img_4 = request.FILES['img_4']
        except:
            pass
        try:
            if request.data['img_5'] == 'null':
                artifact.img_5 = None
            else:
                artifact.img_5 = request.FILES['img_5']
        except:
            pass

        try:
            if request.data['audio_1'] == 'null':
                artifact.audio_1 = None
            else:
                artifact.audio_1 = request.FILES['audio_1']
        except:
            pass
        try:
            if request.data['audio_2'] == 'null':
                artifact.audio_2 = None
            else:
                artifact.audio_2 = request.FILES['audio_2']
        except:
            pass
        try:
            if request.data['audio_3'] == 'null':
                artifact.audio_3 = None
            else:
                artifact.audio_3 = request.FILES['audio_3']
        except:
            pass
        try:
            if request.data['audio_4'] == 'null':
                artifact.audio_4 = None
            else:
                artifact.audio_4 = request.FILES['audio_4']
        except:
            pass
        try:
            if request.data['audio_5'] == 'null':
                artifact.audio_5 = None
            else:
                artifact.audio_5 = request.FILES['audio_5']
        except:
            pass

        # try:
        #     artifact.audio_1 = request.FILES['audio_1']
        # except:
        #     pass

        artifact.link_name_1 = request.data['link_name_1']
        artifact.link_name_2 = request.data['link_name_2']
        artifact.link_name_3 = request.data['link_name_3']
        artifact.link_name_4 = request.data['link_name_4']
        artifact.link_name_5 = request.data['link_name_5']

        artifact.link_value_1 = request.data['link_value_1']
        artifact.link_value_2 = request.data['link_value_2']
        artifact.link_value_3 = request.data['link_value_3']
        artifact.link_value_4 = request.data['link_value_4']
        artifact.link_value_5 = request.data['link_value_5']

        artifact.save()

        return Response(self.get_artifact(request, location_pk, hall_pk, artifact_pk))

    def delete(self, request, location_pk, hall_pk, artifact_pk):
        self.delete_artifact(request, location_pk, hall_pk, artifact_pk)
        return Response(serialize_hall_and_artifacts(request, hall_pk))


class SwapHallsView(APIView):
    """
    Swaps current hall with upper or lower hall
    """
    permission_classes = (IsMuseumAdmin,)

    def swap_and_save_hall(self, swap_type, request):
        if swap_type == 'up':
            cur = Hall.objects.get(pk=request.data['obj_id'])
        elif swap_type == 'down':
            cur = Hall.objects.get(prev=request.data['obj_id'])
        up = Hall.objects.get(pk=cur.prev)
        try:
            down = Hall.objects.get(prev=cur.id)
            cur.prev = None  # deleting obj from list
            down.prev = up.id
            cur.prev = up.prev  # adding obj to list
            up.prev = cur.id
            cur.save()
            up.save()
            down.save()
        except:  # exception only if 'cur' is the last el in the list (then obj 'down' doesn't exists)
            if swap_type == 'down':
                cur = Hall.objects.get(prev=request.data['obj_id'])
                up = Hall.objects.get(pk=request.data['obj_id'])
            cur.prev = up.prev
            up.prev = cur.id
            cur.save()
            up.save()
        return True

    def post(self, request):
        swap_type = request.data['swap_type']
        self.swap_and_save_hall(swap_type, request)
        location_pk = Hall.objects.get(pk=request.data['obj_id']).location.id
        return Response(serialize_location_and_halls(request, location_pk))


def serialize_hall_and_artifacts(request, hall_pk):
    hall = Hall.objects.get(pk=hall_pk)
    hall_serializer = HallSerializer(hall, context={'request': request})

    temp_len = len(Artifact.objects.filter(hall=hall_pk))
    if temp_len > 1:
        list_of_artifacts = list()
        artifact = Artifact.objects.filter(hall=hall_pk).get(prev=None)
        list_of_artifacts.append(artifact)

        for i in range(len(Artifact.objects.filter(hall=hall_pk)) - 1):
            artifact = Artifact.objects.get(prev=artifact.id)
            list_of_artifacts.append(artifact)

        artifacts_serializer = ArtifactSerializer(list_of_artifacts, context={'request': request}, many=True)

        return {
            'hall': hall_serializer.data,
            'artifacts': artifacts_serializer.data
        }
    elif temp_len == 1:
        # location = Location.objects.get(pk=location_pk)
        artifact = Artifact.objects.get(hall=hall_pk)
        artifact_serializer = ArtifactSerializer(artifact, context={'request': request})
        return {
            'hall': hall_serializer.data,
            'artifacts': [artifact_serializer.data]
        }
    else:
        return {
            'hall': hall_serializer.data,
            'artifacts': []
        }


class CurrentHallView(APIView):
    """
    Shows or changes or deletes current hall
    """
    permission_classes = (IsMuseumAdmin,)

    def get_hall(self, request, location_pk, hall_pk):
        return serialize_hall_and_artifacts(request, hall_pk)

    def delete_hall(self, request, location_pk, hall_pk):
        cur = Hall.objects.get(pk=hall_pk)
        try:
            down = Hall.objects.get(prev=cur.id)
            down.prev = cur.prev
            down.save()
        except:
            pass
        cur.delete()
        return True

    def get(self, request, location_pk, hall_pk):
        return Response(self.get_hall(request, location_pk, hall_pk))

    def post(self, request, location_pk, hall_pk):
        name = request.data['name']

        try:
            img_1 = request.FILES['img_1']
        except:
            img_1 = None
        try:
            img_2 = request.FILES['img_2']
        except:
            img_2 = None
        try:
            img_3 = request.FILES['img_3']
        except:
            img_3 = None
        try:
            img_4 = request.FILES['img_4']
        except:
            img_4 = None
        try:
            img_5 = request.FILES['img_5']
        except:
            img_5 = None

        try:
            audio_1 = request.FILES['audio_1']
        except:
            audio_1 = None
        try:
            audio_2 = request.FILES['audio_2']
        except:
            audio_2 = None
        try:
            audio_3 = request.FILES['audio_3']
        except:
            audio_3 = None
        try:
            audio_4 = request.FILES['audio_4']
        except:
            audio_4 = None
        try:
            audio_5 = request.FILES['audio_5']
        except:
            audio_5 = None

        try:
            link_name_1 = request.data['link_name_1']
        except:
            link_name_1 = None
        try:
            link_name_2 = request.data['link_name_2']
        except:
            link_name_2 = None
        try:
            link_name_3 = request.data['link_name_3']
        except:
            link_name_3 = None
        try:
            link_name_4 = request.data['link_name_4']
        except:
            link_name_4 = None
        try:
            link_name_5 = request.data['link_name_5']
        except:
            link_name_5 = None

        try:
            link_value_1 = request.data['link_value_1']
        except:
            link_value_1 = None
        try:
            link_value_2 = request.data['link_value_2']
        except:
            link_value_2 = None
        try:
            link_value_3 = request.data['link_value_3']
        except:
            link_value_3 = None
        try:
            link_value_4 = request.data['link_value_4']
        except:
            link_value_4 = None
        try:
            link_value_5 = request.data['link_value_5']
        except:
            link_value_5 = None

        # audio = request.FILES['audio']
        # video = request.data['video']
        description = request.data['description']
        hall = Hall.objects.get(pk=hall_pk)

        try:
            artifact = Artifact.objects.filter(hall=hall_pk).get(prev=None)
            for i in range(len(Artifact.objects.filter(hall=hall_pk)) - 1):
                artifact = Artifact.objects.get(prev=artifact.id)
            prev = artifact.id
        except:
            prev = None
        aaa = Artifact.create(name=name, description=description, hall=hall, prev=prev,
                              img_1=img_1,
                              img_2=img_2,
                              img_3=img_3,
                              img_4=img_4,
                              img_5=img_5,
                              audio_1=audio_1,
                              audio_2=audio_2,
                              audio_3=audio_3,
                              audio_4=audio_4,
                              audio_5=audio_5,
                              link_name_1=link_name_1,
                              link_name_2=link_name_2,
                              link_name_3=link_name_3,
                              link_name_4=link_name_4,
                              link_name_5=link_name_5,
                              link_value_1=link_value_1,
                              link_value_2=link_value_2,
                              link_value_3=link_value_3,
                              link_value_4=link_value_4,
                              link_value_5=link_value_5,
                              )
        aaa.save()
        return Response(serialize_hall_and_artifacts(request, hall_pk))

    def put(self, request, location_pk, hall_pk):
        hall = Hall.objects.get(pk=hall_pk)

        hall.name = request.data['name']
        hall.save()

        return Response(self.get_hall(request, location_pk, hall_pk))

    def delete(self, request, location_pk, hall_pk):
        self.delete_hall(request, location_pk, hall_pk)
        return Response(serialize_location_and_halls(request, location_pk))


class AllArtifactsView(APIView):
    """
    Shows all artifacts
    """
    permission_classes = (IsMuseumAdmin,)

    def get(self, request):
        artifacts = Artifact.objects.all()
        serializer = ArtifactSerializer(artifacts, context={'request': request}, many=True)
        return Response(serializer.data)


class AllHallsView(APIView):
    """
    Shows all halls
    """
    permission_classes = (IsMuseumAdmin,)

    def get(self, request):
        halls = Hall.objects.all()
        serializer = LocationSerializer(halls, context={'request': request}, many=True)
        return Response(serializer.data)


def swap_and_save_location(swap_type, request):
    if swap_type == 'up':
        cur = Location.objects.get(pk=request.data['obj_id'])
    elif swap_type == 'down':
        cur = Location.objects.get(prev=request.data['obj_id'])
    up = Location.objects.get(pk=cur.prev)
    try:
        down = Location.objects.get(prev=cur.id)
        cur.prev = None  # deleting obj from list
        down.prev = up.id
        cur.prev = up.prev  # adding obj to list
        up.prev = cur.id
        cur.save()
        up.save()
        down.save()
    except:  # exception only if 'cur' is the last el in the list (then obj 'down' doesn't exists)
        if swap_type == 'down':
            cur = Location.objects.get(prev=request.data['obj_id'])
            up = Location.objects.get(pk=request.data['obj_id'])
        cur.prev = up.prev
        up.prev = cur.id
        cur.save()
        up.save()
    return True


class SwapLocationsView(APIView):
    """
    Swaps current location with upper or lower location
    """
    permission_classes = (IsMuseumAdmin,)

    def post(self, request):
        swap_type = request.data['swap_type']
        swap_and_save_location(swap_type, request)
        return Response(serialize_museum_and_locations(request))


def delete_location(request, location_pk):
    cur = Location.objects.get(pk=location_pk)
    try:
        down = Location.objects.get(prev=cur.id)
        down.prev = cur.prev
        down.save()
    except:
        pass
    cur.delete()
    return True


def serialize_location_and_halls(request, location_pk):
    location = Location.objects.get(pk=location_pk)
    location_serializer = LocationSerializer(location, context={'request': request})

    temp_len = len(Hall.objects.filter(location=location_pk))

    if temp_len > 1:
        list_of_halls = list()
        hall = Hall.objects.filter(location=location_pk).get(prev=None)
        list_of_halls.append(hall)

        for i in range(len(Hall.objects.filter(location=location_pk)) - 1):
            hall = Hall.objects.get(prev=hall.id)
            list_of_halls.append(hall)

        halls_serializer = HallSerializer(list_of_halls, context={'request': request}, many=True)
        return {
            'location': location_serializer.data,
            'halls': halls_serializer.data
        }
    elif temp_len == 1:
        # location = Location.objects.get(pk=location_pk)
        hall = Hall.objects.get(location=location)
        halls_serializer = HallSerializer(hall, context={'request': request})
        return {
            'location': location_serializer.data,
            'halls': [halls_serializer.data]
        }
    else:
        return {
            'location': location_serializer.data,
            'halls': []
        }


class CurrentLocationView(APIView):
    """
    Shows or changes or deletes current location
    """
    permission_classes = (IsMuseumAdmin,)

    def get(self, request, location_pk):
        return Response(serialize_location_and_halls(request, location_pk))

    def post(self, request, location_pk):
        name = request.data['name']

        try:
            hall = Hall.objects.filter(location=location_pk).get(prev=None)
            for i in range(len(Hall.objects.filter(location=location_pk)) - 1):
                hall = Hall.objects.get(prev=hall.id)

            location = Location.objects.get(pk=location_pk)
            Hall.objects.create(name=name, location=location, prev=hall.id)
        except:
            location = Location.objects.get(pk=location_pk)
            Hall.objects.create(name=name, location=location, prev=None)

        return Response(serialize_location_and_halls(request, location_pk))

    def put(self, request, location_pk):
        location = Location.objects.get(pk=location_pk)

        location.name = request.data['name']
        location.save()
        return Response(serialize_location_and_halls(request, location_pk))

    def delete(self, request, location_pk):
        delete_location(request, location_pk)
        return Response(serialize_museum_and_locations(request))


class AllLocationsView(APIView):
    """
    Shows all locations
    """
    permission_classes = (IsMuseumAdmin,)

    def get(self, request):
        locations = Location.objects.filter(museum=request.user.museum)
        serializer = LocationSerializer(locations, context={'request': request}, many=True)
        return Response(serializer.data)


def serialize_museum_and_locations(request):
    museum = Museum.objects.get(admins=request.user)
    museum_serializer = MuseumSerializer(museum, context={'request': request})
    is_museum_super_admin = request.user.groups.filter(name='museum_super_admins').exists()

    temp_len = len(Location.objects.filter(museum=request.user.museum))

    if temp_len > 1:
        list_of_locations = list()
        location = Location.objects.filter(museum=request.user.museum).get(prev=None)
        list_of_locations.append(location)

        for i in range(len(Location.objects.filter(museum=request.user.museum)) - 1):
            location = Location.objects.get(prev=location.id)
            list_of_locations.append(location)

        locations_serializer = LocationSerializer(list_of_locations, context={'request': request}, many=True)

        return {
            'museum': museum_serializer.data,
            'is_museum_super_admin': is_museum_super_admin,
            'locations': locations_serializer.data
        }
    elif temp_len == 1:
        location = Location.objects.get(museum=request.user.museum)
        locations_serializer = LocationSerializer(location, context={'request': request})
        return {
            'museum': museum_serializer.data,
            'is_museum_super_admin': is_museum_super_admin,
            'locations': [locations_serializer.data]
        }
    else:
        return {
            'museum': museum_serializer.data,
            'is_museum_super_admin': is_museum_super_admin,
            'locations': []
        }


class CurrentMuseumView(APIView):
    """
    Shows or changes current museum
    """

    # permission_classes = (IsAuthenticated,)
    permission_classes = (IsMuseumAdmin,)

    def get(self, request):
        return Response(serialize_museum_and_locations(request))

    def post(self, request):
        name = request.data['name']

        try:
            location = Location.objects.filter(museum=request.user.museum).get(prev=None)
            for i in range(len(Location.objects.filter(museum=request.user.museum)) - 1):
                location = Location.objects.get(prev=location.id)

            Location(name=name, museum=request.user.museum,
                     prev=location.id).save()
        except:
            Location(name=name, museum=request.user.museum,
                     prev=None).save()

        return Response(serialize_museum_and_locations(request))

    def put(self, request):
        museum = Museum.objects.get(pk=request.user.museum.id)

        museum.name = request.data['name']
        museum.description = request.data['description']
        museum.ticket_lifetime = request.data['ticket_lifetime']
        try:
            museum.img = request.FILES['img']
        except:
            pass
        museum.save()

        return Response(serialize_museum_and_locations(request))


class MuseumSuperAdminView(APIView):
    """
    # Shows all museums, creates new one or deletes current
    """
    permission_classes = (IsServiceSuperAdmin,)

    def get_museum_super_admin(self, request, museum_pk):
        museum = Museum.objects.get(pk=museum_pk)
        museum_serializer = MuseumSerializer(museum, context={'request': request})

        users = User.objects.filter(museum=museum_pk).exclude(pk=request.user.id)
        for user in users:
            if user.groups.filter(name='museum_super_admins').exists():
                museum_super_admin = user
                break
        try:
            museum_super_admin_serializer = UserSerializer(museum_super_admin, context={'request': request})
            return {
                'status': True,
                'museum_super_admin': museum_super_admin_serializer.data,
                'museum': museum_serializer.data
            }
        except:
            return {
                'status': False,
                'museum_super_admin': {},
                'museum': museum_serializer.data
            }

    def get(self, request, museum_pk):
        return Response(self.get_museum_super_admin(request, museum_pk))

    def post(self, request, museum_pk):
        username = request.data['email']
        email = request.data['email']
        password = request.data['password']
        last_name = request.data['last_name']
        first_name = request.data['first_name']
        middle_name = request.data['middle_name']

        # username = 'm_super_1'
        # email = 'email'
        # password = 'password'
        # last_name = 'Chentsov'
        # first_name = 'Alex'
        # middle_name = ''

        users = User.objects.filter(museum=museum_pk).exclude(pk=request.user.id)
        for user in users:
            if user.groups.filter(name='museum_super_admins').exists():
                return Response(
                    {"error_code": 'MUSEUM SUPER ADMIN IS ALREADY EXISTS', "status": status.HTTP_403_FORBIDDEN})

        museum = Museum.objects.get(pk=museum_pk)

        user = User.objects.create_user(username=username, password=password, last_name=last_name,
                                        first_name=first_name, middle_name=middle_name,
                                        email=email, museum=museum)

        group = Group.objects.get(name='museum_super_admins')
        user.groups.add(group.id)
        group = Group.objects.get(name='museum_admins')
        user.groups.add(group.id)
        user.save()
        return Response(self.get_museum_super_admin(request, museum_pk))

    def delete(self, request, museum_pk):
        users = User.objects.filter(museum=museum_pk).exclude(pk=request.user.id)
        for user in users:
            if user.groups.filter(name='museum_super_admins').exists() or user.groups.filter(
                    name='museum_admins').exists() or user.groups.filter(name='museum_cashiers').exists():
                user.delete()
                return Response(self.get_museum_super_admin(request, museum_pk))
        return Response(
            {"error_code": 'MUSEUM SUPER ADMIN DOES NOT EXISTS', "status": status.HTTP_404_NOT_FOUND})


class MuseumsView(APIView):
    """
    Shows all museums, creates new one or deletes current
    """
    permission_classes = (IsServiceSuperAdmin,)

    def get_all_museums(self, request):
        museums = Museum.objects.all()
        serializer = MuseumSerializer(museums, context={'request': request}, many=True)
        return serializer.data

    def get(self, request):
        return Response(self.get_all_museums(request))

    def post(self, request):
        name = request.data['name']
        img = request.data['img']
        description = request.data['description']

        Museum.objects.create(name=name, img=img, description=description)

        return Response(self.get_all_museums(request))

    def delete(self, request):
        museum_pk = request.data['museum_pk']
        try:
            museum = Museum.objects.get(pk=museum_pk)
            museum.delete()
            return Response(self.get_all_museums(request))
        except:
            return Response({"error_code": 'MUSEUM DOES NOT EXISTS', "status": status.HTTP_404_NOT_FOUND})


class MuseumProfilesView(APIView):
    """
    Shows/creates/deletes employees of current museum
    """
    permission_classes = (IsMuseumSuperAdmin,)

    def get_users(self, request):
        museum_super_admin = User.objects.get(pk=request.user.id)
        users = User.objects.filter(museum=request.user.museum).exclude(pk=request.user.id)

        museum_admins = list()
        museum_cashiers = list()
        for user in users:
            if user.groups.filter(name='museum_admins').exists():
                museum_admins.append(user)
            elif user.groups.filter(name='museum_cashiers').exists():
                museum_cashiers.append(user)

        museum_super_admin_serializer = UserSerializer(museum_super_admin, context={'request': request})
        museum_admins_serializer = UserSerializer(museum_admins, context={'request': request}, many=True)
        museum_cashiers_serializer = UserSerializer(museum_cashiers, context={'request': request}, many=True)
        return {'museum_super_admin': museum_super_admin_serializer.data,
                'museum_admins': museum_admins_serializer.data,
                'museum_cashiers': museum_cashiers_serializer.data
                }

    def get(self, request):
        return Response(self.get_users(request))

    def post(self, request):
        username = request.data['email']
        email = request.data['email']
        password = request.data['password']
        last_name = request.data['last_name']
        first_name = request.data['first_name']
        middle_name = request.data['middle_name']
        role = request.data['role']

        # username = 'm_cashier_2'
        # email = 'email'
        # password = 'password'
        # last_name = 'Chentsov'
        # first_name = 'Alex'
        # middle_name = ''
        # role = 'museum_cashiers'

        user = User.objects.create_user(username=username, password=password, last_name=last_name,
                                        first_name=first_name, middle_name=middle_name,
                                        email=email, museum=request.user.museum)
        if role == 'museum_admins':
            group = Group.objects.get(name='museum_admins')
        elif role == 'museum_cashiers':
            group = Group.objects.get(name='museum_cashiers')
        user.groups.add(group.id)
        user.save()
        return Response(self.get_users(request))

    def put(self, request, user_pk):
        museum_super_admin = request.user
        user = User.objects.get(pk=user_pk)

        if museum_super_admin.museum == user.museum:
            user.last_name = request.data['last_name']
            user.first_name = request.data['first_name']
            user.middle_name = request.data['middle_name']
            user.email = request.data['email']
            user.username = request.data['email']

            # user.last_name = 'last'
            # user.first_name = 'first'
            # user.middle_name = 'middle'
            # user.email = 'email'
            # user.username = 'username'
            user.save()

            return Response(self.get_users(request))
        else:
            return Response({"error_code": 'ERROR', "status": status.HTTP_403_FORBIDDEN})

    def delete(self, request, user_pk):
        museum_super_admin = request.user
        user = User.objects.get(pk=user_pk)

        if user.id != museum_super_admin.id:
            if museum_super_admin.museum == user.museum:
                user.delete()
                return Response(self.get_users(request))
            else:
                return Response({"error_code": 'ERROR', "status": status.HTTP_403_FORBIDDEN})
        else:
            return Response({"error_code": 'ERROR', "status": status.HTTP_403_FORBIDDEN})


class ReactAppView(View):

    def get(self, request):
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        try:
            with open(os.path.join(BASE_DIR, 'frontend', 'build', 'index.html')) as file:
                return HttpResponse(file.read())

        except:
            return HttpResponse(
                """
                File index.html not found ! Build your React app !
                """,
                status=501,
            )

# validating data
# def post(self, request):
#     user = request.data
#     serializer = UserSerializer(data=user)
#     serializer.is_valid(raise_exception=True)
#     serializer.save()
#     return Response({"user": serializer.data, "status": status.HTTP_200_OK})
