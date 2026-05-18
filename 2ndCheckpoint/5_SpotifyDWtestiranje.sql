USE spotify_dw;

SELECT 
            u.user_id,
            c.name AS country,
            u.age,
            u.signup_date,
            s.name AS subscription_type,
            u.subscription_status,
            u.months_inactive,
            u.inactive_3_months_flag,
            u.ad_interaction,
            u.ad_conversion AS ad_conversion_to_subscription,
            u.suggestion_rating AS music_suggestion_rating_1_to_5,
            u.listening_hours AS avg_listening_hours_per_week,
            g.name AS favorite_genre,
            f1.name AS most_liked_feature,
            f2.name AS desired_future_feature,
            d.name AS primary_device,
            u.playlists_created,
            u.skips_per_day AS avg_skips_per_day
        FROM users u
        JOIN countries c ON u.country_id = c.id
        JOIN subscription_types s ON u.sub_type_id = s.id
        JOIN genres g ON u.genre_id = g.id
        JOIN devices d ON u.device_id = d.id
        JOIN features f1 ON u.liked_feature_id = f1.id
        JOIN features f2 ON u.desired_feature_id = f2.id
        ORDER BY u.user_id ASC;


SELECT * FROM features ORDER BY id ASC;

SELECT * FROM features;

# --- FUNKCIONALNOST "AI DJ" korisnici I VOLE I ŽELE U ISTO VRIJEME 
# --- (to može značiti da je u nekim područjima taj feature postojeći ili za neke modele pretplate postojeći a za neke nije)
SELECT 
    f.name AS 'Naziv funkcionalnosti',
    COALESCE(liked.suma_voli, 0) AS 'Broj korisnika koji VOLE',
    COALESCE(desired.suma_zele, 0) AS 'Broj korisnika koji ZELE'
FROM features f
LEFT JOIN (
    SELECT liked_feature_id, COUNT(*) as suma_voli 
    FROM users 
    GROUP BY liked_feature_id
) liked ON f.id = liked.liked_feature_id
LEFT JOIN (
    SELECT desired_feature_id, COUNT(*) as suma_zele 
    FROM users 
    GROUP BY desired_feature_id
) desired ON f.id = desired.desired_feature_id
ORDER BY (COALESCE(liked.suma_voli, 0) + COALESCE(desired.suma_zele, 0)) DESC;