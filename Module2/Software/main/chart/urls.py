from django.urls import path

from . import views

urlpatterns = [
	path("",views.main, name="main"),
	path("compute_graph",views.compute_graph, name="compute_graph"),
	path("close_app",views.close_app, name="close_app"),
	path("filter_life_assessment.html",views.filter_main_la, name="compute_graph"),
	path("main_life_assessment.html",views.main_la, name="main_life_assessment"),
	path("restore_main_life_assessment.html",views.restore_main_la, name="restore_main_life_assessment"),
	path("filter_economic_impact.html",views.filter_main_ei, name="compute_graph"),
	path("main_economic_impact.html",views.main_ei, name="main_economic_impact"),
	path("restore_main_economic_impact.html",views.restore_main_ei, name="restore_main_economic_impact"),
	path("filter_maintenance_strategy.html",views.filter_main_ms, name="compute_graph"),
	path("main_maintenance_strategy.html",views.main_ms, name="main_maintenance_strategy"),
	path("restore_main_maintenance_strategy.html",views.restore_main_ms, name="restore_main_maintenance_strategy"),
]
