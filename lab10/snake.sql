CREATE TABLE IF NOT EXISTS players (
  player_id SERIAL PRIMARY KEY,
  player_name VARCHAR(50) UNIQUE NOT NULL,
  date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS player_scores (
  score_id SERIAL PRIMARY KEY,
  player_id INTEGER REFERENCES players(player_id),
  score INTEGER NOT NULL,
  level INTEGER NOT NULL,
  game_duration INTEGER NOT NULL,
  date_recorded TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_player_scores_score ON player_scores(score);
CREATE INDEX IF NOT EXISTS idx_player_scores_plater ON player_scores(player_id);
