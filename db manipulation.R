#install.packages("RMySQL")
library(RMySQL)

mydb = dbConnect(MySQL(), default.file='C:/Users/jadetooth/SkyDrive/Documents/CarbonWA/dbssh/params_j.txt')
dbGetQuery(mydb, 'CREATE TABLE entries (
  entryID INT NOT NULL AUTO_INCREMENT,
  guestName VARCHAR(255),
  content VARCHAR(255),
  PRIMARY KEY(entryID)
);')
dbGetQuery(mydb, 'select * from signatures limit 20')

dbGetQuery(mydb, 'CREATE TABLE voters (
  statevoterid nvarchar(15),
  fname nvarchar(50),
  mname nvarchar(50),
  lname nvarchar(50),
  namesuffix nvarchar(10),
  birthdate date,
  gender varchar(1),
  address nvarchar(100),
  city nvarchar(50),
  state varchar(2),
  zip nvarchar(15),
  countycode varchar(2),
  regdate date,
  latevoted date,
  statuscode nvarchar(10),
  PRIMARY KEY(statevoterid)
);')

dbGetQuery(mydb, "CREATE INDEX lastfirstcounty ON voters (lname, fname, countycode)")
dbGetQuery(mydb, "CREATE INDEX lastmidcitycounty ON voters (lname, mname, city, countycode)")
dbGetQuery(mydb, "CREATE INDEX lastcity ON voters (lname, city)")
dbGetQuery(mydb, "CREATE INDEX lastcounty ON voters (lname, countycode)")

dbGetQuery(mydb, "
LOAD DATA LOCAL INFILE 'C:/Users/jadetooth/SkyDrive/Documents/CarbonWA/voters_reduced.csv' 
INTO TABLE voters 
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
")

dbGetQuery(mydb, 'CREATE TABLE counties (
  countycode varchar(2),
  county nvarchar(30),
  PRIMARY KEY(county, countycode)
);')

dbGetQuery(mydb, "insert into counties values
           ('AD', 'Adams'),
           ('AS', 'Asotin'),
           ('BE', 'Benton'),
           ('CH', 'Chelan'),
           ('CM', 'Clallam'),
           ('CR', 'Clark'),
           ('CU', 'Columbia'),
           ('CZ', 'Cowlitz'),
           ('DG', 'Douglas'),
           ('FE', 'Ferry'),
           ('FR', 'Franklin'),
           ('GA', 'Garfield'),
           ('GR', 'Grant'),
           ('GY', 'Grays Harbor'),
           ('IS', 'Island'),
           ('JE', 'Jefferson'),
           ('KI', 'King'),
           ('KP', 'Kitsap'),
           ('KS', 'Kittitas'),
           ('KT', 'Klickitat'),
           ('LE', 'Lewis'),
           ('LI', 'Lincoln'),
           ('MA', 'Mason'),
           ('OK', 'Okanogan'),
           ('PA', 'Pacific'),
           ('PE', 'Pend Oreille'),
           ('PI', 'Pierce'),
           ('SJ', 'San Juan'),
           ('SK', 'Skagit'),
           ('SM', 'Skamania'),
           ('SN', 'Snohomish'),
           ('SP', 'Spokane'),
           ('ST', 'Stevens'),
           ('TH', 'Thurston'),
           ('WK', 'Wahkiakum'),
           ('WL', 'Walla Walla'),
           ('WM', 'Whatcom'),
           ('WT', 'Whitman'),
           ('YA', 'Yakima')
           ;")

dbGetQuery(mydb, 'update counties set county=lower(county);')

dbGetQuery(mydb, 'create view vw_voter as
           select 
           statevoterid,
           fname,
           mname,
           lname,
           concat(fname, " ", mname, " ", lname) as name,
           address,
           city,
           county,
           birthdate
           from voters inner join counties on
           voters.countycode = counties.countycode;')

#dbGetQuery(mydb, 'drop view vw_voter')

#dbGetQuery(mydb, 'drop table signers;')
dbGetQuery(mydb, 'create table signers (
           statevoterid nvarchar(15) NULL,
           fname nvarchar(50) NULL,
           lname nvarchar(50) NULL,
           city nvarchar(50) NULL,
           county nvarchar(30) NULL,
           signed boolean,
           createdby nvarchar(50),
           createddate datetime
           );')
dbGetQuery(mydb, "CREATE INDEX voterid ON signers (statevoterid)")

#dbGetQuery(mydb, 'drop table users;')
dbGetQuery(mydb, 'create table users (
           email varchar(50),
           primary key (email)
           );')

dbGetQuery(mydb, 'insert into users value ("carroll.joshk@gmail.com");')

#dbGetQuery(mydb, 'drop table admins;')
dbGetQuery(mydb, 'create table admins (
           userid varchar(30),
           primary key (userid)
           );')

#Josh
dbGetQuery(mydb, 'insert into admins value ("105168972660145900096");')
#Kyle
dbGetQuery(mydb, 'insert into admins value ("100701096175130837417");')
#Duncan
dbGetQuery(mydb, 'insert into admins value ("116373179634861946390");')

dbGetQuery(mydb, 'select * from admins;')
#dbDisconnect(mydb)

dbGetQuery(mydb, 'create table signatures (
           sheet integer,
           entry integer,
           fname nvarchar(50) NULL,
           lname nvarchar(50) NULL,
           streetnum integer NULL,
           city nvarchar(50) NULL,
           county nvarchar(30) NULL,
           scan nvarchar(10),
           primary key (scan, sheet, entry)
           );')