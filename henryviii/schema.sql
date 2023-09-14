DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);


DROP TABLE IF EXISTS off_account_list;
DROP TABLE IF EXISTS off_account_article;

CREATE TABLE off_account_list (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL,
  category TEXT,
  article_updated_at DATETIME,
  registered_at INTEGER
);

CREATE TABLE off_account_article (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  off_account_name TEXT NOT NULL,
  title TEXT,
  updated_at DATETIME,
  content BLOB,
  link TEXT,
  registered_at INTEGER
);

DROP TABLE IF EXISTS off_account_followed;
CREATE TABLE off_account_followed (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  off_account_name TEXT NOT NULL,
  username TEXT NOT NULL,
  updated_at DATETIME NOT NULL
);



-- DROP TABLE IF EXISTS off_account_article_user_meta;
-- CREATE TABLE off_account_article_user_meta (
--   id INTEGER PRIMARY KEY AUTOINCREMENT,
--   off_account_article_id INTEGER NOT NULL,
--   username TEXT NOT NULL,
--   viewed_at DATETIME,
--   liked_at DATETIME,
--   deleted_at DATETIME,
--   UNIQUE(off_account_article_id, username)
-- );
CREATE TABLE off_account_article_viewed (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  off_account_article_id INTEGER NOT NULL,
  username TEXT NOT NULL,
  updated_at DATETIME NOT NULL,
  UNIQUE(off_account_article_id, username)
);

-- ALTER TABLE


DROP TABLE IF EXISTS off_account_article_liked;
CREATE TABLE off_account_article_liked (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  off_account_article TEXT NOT NULL,
  username TEXT NOT NULL,
  updated_at DATETIME
);

DROP TABLE IF EXISTS off_account_article_deleted;
CREATE TABLE off_account_article_deleted (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  off_account_article TEXT NOT NULL,
  username TEXT NOT NULL,
  updated_at DATETIME NOT NULL
);