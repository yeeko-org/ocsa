SELECT "space_time_location"."id", "space_time_location"."project_id", "space_time_location"."event_id", "space_time_location"."impact_id", "space_time_location"."state_id", "space_time_location"."municipality_id", "space_time_location"."locality_id", "space_time_location"."details", "space_time_location"."latitude", "space_time_location"."longitude", "space_time_location"."geojson", "space_time_location"."type_location", "space_time_location"."ubicacion_id_ref", "space_time_location"."status_location_id", "space_time_location"."comments", "project_project"."id", "project_project"."proyecto_id_ref", "project_project"."legacy_id_mp", "project_project"."name", "project_project"."alternative_name", "project_project"."description", "project_project"."parent_project_id", "project_project"."conflict_id", "project_project"."megaproject_type_id", "project_project"."is_grouper", "project_project"."status_project_id", "project_project"."status_validation_id", "project_project"."status_location_id", "project_project"."comments" FROM "space_time_location"
	INNER JOIN "project_project" ON ("space_time_location"."project_id" = "project_project"."id")
	INNER JOIN "work_flux_statuscontrol" ON ("space_time_location"."status_location_id" = "work_flux_statuscontrol"."name") 

	WHERE (("space_time_location"."project_id" IS NOT NULL AND "work_flux_statuscontrol"."is_public" AND "space_time_location"."latitude" IS NOT NULL AND "space_time_location"."longitude" IS NOT NULL AND "space_time_location"."type_location" = point) OR ("space_time_location"."project_id" IS NOT NULL AND "work_flux_statuscontrol"."is_public" AND "space_time_location"."geojson" IS NOT NULL AND NOT ("space_time_location"."type_location" = point)))



19.05583080250534
19.05574355463108
