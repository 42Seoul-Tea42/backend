DROP TABLE IF EXISTS "History";
DROP TABLE IF EXISTS "Chat";
DROP TABLE IF EXISTS "Block";
DROP TABLE IF EXISTS "Report";
DROP TABLE IF EXISTS "User";

CREATE TABLE "User" (
  	"id"        SERIAL PRIMARY KEY,
	"login_id"	TEXT	UNIQUE,-- NOT NULL 필요? oauth 유저와 원만한 합의 필요
	"password"	TEXT,
  	"email"	    TEXT	UNIQUE NOT NULL,
	"email_check"	BOOLEAN	NOT NULL,
	"email_key"	TEXT,
	"refresh_token" TEXT,
	"name"	    TEXT	NOT NULL,
	"last_name"	TEXT,
	"birthday"	DATE,
	"last_online"	TIMESTAMP,
	"longitude"	FLOAT,
    "latitude"	FLOAT,
	"count_view" INTEGER,
	"count_fancy" INTEGER,
	"gender"	  INTEGER,
	"pictures"	TEXT[],
	"taste"	    INTEGER,
	"bio"	      TEXT,
	"tags"	    INTEGER,
	"hate_tags"	INTEGER,
	"emoji"	    INTEGER,
	"hate_emoji"	INTEGER,
	"similar"	  BOOLEAN
);

CREATE TABLE "History" (
	"user_id"	  INTEGER	NOT NULL,
	"target_id"	INTEGER	NOT NULL,
	"fancy"	    BOOLEAN NOT NULL,
	"fancy_time"	TIMESTAMP,
	"fancy_check"	BOOLEAN,
	"last_view"	TIMESTAMP	NOT NULL,
  PRIMARY KEY (user_id, target_id),
  FOREIGN KEY (user_id) REFERENCES "User" (id) ON DELETE CASCADE,
  FOREIGN KEY (target_id) REFERENCES "User" (id) ON DELETE CASCADE
);

CREATE TABLE "Chat" (
	"id"        SERIAL PRIMARY KEY,
	"user_id"	  INTEGER	NOT NULL,
	"target_id"	INTEGER	NOT NULL,
	"msg"	      TEXT,
  	"msg_time"  TIMESTAMP	NOT NULL,
	"msg_check"	BOOLEAN	NOT NULL,
  FOREIGN KEY (user_id) REFERENCES "User" (id) ON DELETE CASCADE,
  FOREIGN KEY (target_id) REFERENCES "User" (id) ON DELETE CASCADE
);

CREATE TABLE "Block" (
	"user_id"	  INTEGER	NOT NULL,
	"target_id"	INTEGER	NOT NULL,
  PRIMARY KEY (user_id, target_id),
  FOREIGN KEY (user_id) REFERENCES "User" (id) ON DELETE CASCADE,
  FOREIGN KEY (target_id) REFERENCES "User" (id) ON DELETE CASCADE
);

CREATE TABLE "Report" (
	"user_id"	  INTEGER	NOT NULL,
	"target_id"	INTEGER	NOT NULL,
	"reason"	  INTEGER	NOT NULL,
	"reason_opt"	TEXT,
  PRIMARY KEY (user_id, target_id),
  FOREIGN KEY (user_id) REFERENCES "User" (id) ON DELETE CASCADE,
  FOREIGN KEY (target_id) REFERENCES "User" (id) ON DELETE CASCADE
);
