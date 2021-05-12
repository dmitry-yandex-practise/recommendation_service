CREATE SCHEMA IF NOT EXISTS recommendations;


CREATE TABLE IF NOT EXISTS recommendations.recommendations (
    user_id uuid PRIMARY KEY,
    recommendations jsonb
);


INSERT INTO recommendations.recommendations
(user_id, recommendations)
VALUES ('77dacbc1-eecd-422d-a68c-39021e033082', '{"must_watch": ["93a1b3e2-1090-497e-863c-e4d634a5c14b"]}');