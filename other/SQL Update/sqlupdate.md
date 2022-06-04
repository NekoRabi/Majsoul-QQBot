# 0.6.0-alpha

---

TenHouPlugin (最好是直接删库，重新生成)
```

ALTER TABLE group2player ADD COLUMN iswatching integer not null default 1;

ALTER TABLE watchedplayer ADD COLUMN watchedgroupcount integer not null default 0;

UPDATE watchedplayer SET watchedgroupcount = (select count(iswatching) from group2player where watchedplayer.playerid = group2player.playerid);

create view if not exists groupwatches as select groupid,group_concat(playername) as watchedplayers,count(groupid) as watchnums from group2player where iswatching = 1 group by groupid```

```
MajSoulInfo (最好是直接删库，重新生成)

```

ALTER TABLE watchedplayer ADD COLUMN watchedgroupcount integer not null default 0;

ALTER TABLE group2player ADD COLUMN iswatching integer not null default 1;

UPDATE watchedplayer SET watchedgroupcount = (select count(iswatching) from group2player where watchedplayer.playerid = group2player.playerid);

create view if not exists groupwatches as select groupid,group_concat(playername) as watchedplayers,count(groupid) as watchnums from group2player where iswatching = 1 group by groupid```

```

LeisurePlugin

```

ALTER TABLE userinfo ADD COLUMN keepsigndays integer not null default 1;

create table IF NOT EXISTS tarot (id integer primary key,cardsid integer,cardname varchar(40) not null,position int not null default 1 )

```

# 0.6.0-beta
TenHouPlugin
```
create view if not exists watchedplayersview as select playername,count(groupid) as watchedgroupcount from group2player where iswatching = 1 group by playername
```


MajSoulInfo


```
create view if not exists watchedplayersview as select playername,playerid, count(groupid) as watchedgroupcount from group2player where iswatching = 1 group by playername")

```
