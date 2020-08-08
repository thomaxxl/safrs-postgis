\c safrs
CREATE EXTENSION postgis;
CREATE TABLE cities (
    point_id SERIAL PRIMARY KEY,
    location VARCHAR(30),
    latitude FLOAT,
    longitude FLOAT,
    geo geometry(POINT)
);

INSERT INTO cities (location, latitude, longitude, geo) VALUES ('San Bruno', 37.6305, -122.4111, 'POINT(-122.4111 37.6305)');
