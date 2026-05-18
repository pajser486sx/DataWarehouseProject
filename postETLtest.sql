SELECT * FROM spotify_dw.fact_user_activity LIMIT 10;

SELECT country_tk, COUNT(*) FROM spotify_dw.fact_user_activity GROUP BY country_tk;

SELECT * FROM spotify_dw.dim_country WHERE country_tk = 1;
SELECT * FROM spotify_dw.dim_country WHERE country_tk = 4;