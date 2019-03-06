from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path('', views.home, name='NMR-home'),
    path('about/', views.about, name='NMR-about'),
    path('predict/', views.predict, name='NMR-predict'),
    path('sketcher/', TemplateView.as_view(template_name="NMR_Prediction/sketcher.html"),
                   name='sketcher'),
    path('NNPredict/', views.NNPredict, name='NMR-NN-Predict'),
    path('JSmol_startup/', views.JSmol_startup, name='JSmol_startup'),
    path('Shift_startup/', views.Shift_startup, name='Shift_startup'),
]
