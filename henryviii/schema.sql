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


-- correct script

-- PRAGMA foreign_keys=off;

-- BEGIN TRANSACTION;

-- ALTER TABLE off_account_user_meta
--  RENAME TO off_account_user_meta_old;

-- CREATE TABLE off_account_user_meta (
--   id INTEGER PRIMARY KEY AUTOINCREMENT,
--   off_account_name TEXT NOT NULL,
--   off_account_id INTEGER NOT NULL,
--   username TEXT NOT NULL,
--   followed_at DATETIME,
--   user_category TEXT,
--   UNIQUE(off_account_name, username)
-- );

-- INSERT INTO off_account_user_meta 
--   SELECT oaum.id, oaum.off_account_name, oal.id as off_account_id, oaum.username, oaum.followed_at, oaum.user_category
--    FROM off_account_user_meta_old oaum
--    LEFT JOIN off_account_list oal
--    ON oaum.off_account_name = oal.name;

-- COMMIT;

-- PRAGMA foreign_keys=on;


-- 
-- update for 20230915
-- 
-- depreciated table
-- DROP TABLE IF EXISTS off_account_followed;
-- CREATE TABLE off_account_followed (
--   id INTEGER PRIMARY KEY AUTOINCREMENT,
--   off_account_name TEXT NOT NULL,
--   username TEXT NOT NULL,
--   updated_at DATETIME NOT NULL
-- );


--
-- migrate off_account_followed to off_account_user_meta
-- 

PRAGMA foreign_keys=off;

BEGIN TRANSACTION;

ALTER TABLE off_account_followed
ADD user_category TEXT;

-- ALTER TABLE off_account_followed
-- RENAME COLUMN updated_at TO followed_at;

CREATE TABLE off_account_user_meta (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  off_account_name TEXT NOT NULL,
  off_account_id INTEGER NOT NULL,
  username TEXT NOT NULL,
  followed_at DATETIME,
  user_category TEXT,
  UNIQUE(off_account_name, username)
);

INSERT INTO off_account_user_meta 
 SELECT oaf.id, oaf.off_account_name, oal.id as off_account_id, oaf.username, oaf.updated_at as followed_at
  FROM off_account_followed oaf
  LEFT JOIN off_account_list oal
  ON oaf.off_account_name = oal.name;

ALTER TABLE off_account_followed RENAME TO off_account_followed_old;

COMMIT;

PRAGMA foreign_keys=on;
-----






-- debug

INSERT INTO user_meta(username, meta_key, meta_info) VALUES ("alfredhwu", "user_category", "新分类#1|新分类#2");


-- end config









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