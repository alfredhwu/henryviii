DROP TABLE IF EXISTS user;
CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

DROP TABLE IF EXISTS off_account_list;
CREATE TABLE off_account_list (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL,
  category TEXT,
  article_updated_at DATETIME,
  registered_at INTEGER
);


DROP TABLE IF EXISTS off_account_article;
CREATE TABLE off_account_article (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  off_account_name TEXT NOT NULL,
  title TEXT,
  updated_at DATETIME,
  content BLOB,
  link TEXT,
  registered_at INTEGER
);

-- new table
DROP TABLE IF EXISTS user_meta;
CREATE TABLE user_meta (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL,
  meta_key TEXT NOT NULL,
  meta_info TEXT NOT NULL,
  UNIQUE(username, meta_key)
);

-- new table
DROP TABLE IF EXISTS off_account_user_meta;
CREATE TABLE off_account_user_meta (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  off_account_name TEXT NOT NULL,
  off_account_id INTEGER NOT NULL,
  username TEXT NOT NULL,
  followed_at DATETIME,
  user_category TEXT,
  UNIQUE(off_account_name, username)
);

CREATE TABLE off_account_article_viewed (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  off_account_article_id INTEGER NOT NULL,
  username TEXT NOT NULL,
  updated_at DATETIME NOT NULL,
  UNIQUE(off_account_article_id, username)
);