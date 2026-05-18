USE spotify_dw;
# POČETAK TESTIRANJA - countries
SELECT 
    f.fact_tk,
    d.full_date AS Datum_Registracije,
    c.name AS Drzava,
    c.continent AS Kontinent,
    s.type_name AS Tip_Pretplate,
    s.status AS Status_Pretplate,
    e.device_name AS Uređaj,
    f.listening_hours AS Sati_Slusanja,
    f.age AS Godine
FROM spotify_dw.fact_user_activity f
JOIN spotify_dw.dim_date d ON f.date_tk = d.date_tk
JOIN spotify_dw.dim_country c ON f.country_tk = c.country_tk
JOIN spotify_dw.dim_subscription s ON f.subscription_tk = s.subscription_tk
JOIN spotify_dw.dim_engagement e ON f.engagement_tk = e.engagement_tk
LIMIT 50;

SELECT DISTINCT name 
FROM spotify_dw.countries 
ORDER BY name;

SELECT name FROM spotify_dw.dim_country WHERE continent IS NULL;

# DATE TESTIRANJE - provjera broja registracija po kvartalima i godinama
SELECT 
    year, 
    quarter, 
    month_name, 
    COUNT(*) as broj_registracija
FROM spotify_dw.dim_date
GROUP BY year, quarter, month_name
ORDER BY year DESC, quarter DESC;

# PRETPLATE TEST - prikaz svih jedinstvenih stanja pretplate i koliko korisnika ih koristi
SELECT 
    s.type_name, 
    s.status, 
    COUNT(f.fact_tk) as broj_korisnika
FROM spotify_dw.fact_user_activity f
JOIN spotify_dw.dim_subscription s ON f.subscription_tk = s.subscription_tk
GROUP BY s.type_name, s.status
ORDER BY broj_korisnika DESC;

# ENGAGEMENT TEST - koji uređaji imaju najbolji rating glazbenih preporuka
SELECT 
    e.device_name, 
    AVG(f.suggestion_rating) as prosjecna_ocjena,
    COUNT(*) as broj_zapisa
FROM spotify_dw.fact_user_activity f
JOIN spotify_dw.dim_engagement e ON f.engagement_tk = e.engagement_tk
GROUP BY e.device_name
ORDER BY prosjecna_ocjena DESC;

