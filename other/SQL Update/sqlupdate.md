# 2022/5/24

---

TenHouPlugin
```
ALTER TABLE group2player ADD COLUMN iswatching integer not null default 1;
ALTER TABLE watchedplayer ADD COLUMN iswatching integer not null default 1;
```

MajSoulInfo
```

ALTER TABLE watchedplayer ADD COLUMN iswatching integer not null default 1;

ALTER TABLE group2player ADD COLUMN iswatching integer not null default 1;

```
LeisurePlugin
```

ALTER TABLE userinfo ADD COLUMN keepsigndays integer not null default 1;

create table IF NOT EXISTS tarot (id integer primary key,cardsid integer,cardname varchar(40) not null,position int not null default 1 )

```
