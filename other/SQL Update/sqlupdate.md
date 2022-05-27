# 2022/5/24

---

TenHouPlugin (最好是直接删库，重新生成)
```
ALTER TABLE group2player ADD COLUMN iswatching integer not null default 1;
ALTER TABLE watchedplayer ADD COLUMN watchedgroupcount integer not null default 0;

```

MajSoulInfo (最好是直接删库，重新生成)
```

ALTER TABLE watchedplayer ADD COLUMN watchedgroupcount integer not null default 0;

ALTER TABLE group2player ADD COLUMN iswatching integer not null default 1;

```
LeisurePlugin
```

ALTER TABLE userinfo ADD COLUMN keepsigndays integer not null default 1;

create table IF NOT EXISTS tarot (id integer primary key,cardsid integer,cardname varchar(40) not null,position int not null default 1 )

```
