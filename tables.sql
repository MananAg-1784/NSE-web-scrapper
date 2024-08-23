use stock_data;

create table if not exists prices(
	stock_id int,
    date date,
    open float,
    close float,
    high float,
    low float,
    vwap float,
    volume decimal(50,4),
    value decimal(50,4),
    no_of_trades bigint,
    primary key(stock_id, date),
    foreign key (stock_id) references stocks(stock_id)
);

create table if not exists sectors(
	sector_id int primary key auto_increment,
    sector varchar(100) not null unique
);

create table if not exists industry(
	industry_id int primary key auto_increment,
    industry varchar(100) not null unique
);

create table if not exists indices(
	indice_id int primary key auto_increment,
    indices varchar(100) not null unique
);

create table if not exists stocks(
	stock_id int primary key auto_increment,
    symbol varchar(50) not null unique,
    company_name varchar(200) not null unique,
    listing_date date,
    isin_code varchar(50) not null unique,
    market_cap bigint, 	-- (In Crores)
    sector_id int not null,
    industry_id int not null,
    foreign key (sector_id) references sectors(sector_id),
    foreign key (industry_id) references industry(industry_id)
);

create table if not exists stock_indices(
	stock_id int not null,
    indice_id int not null,
    primary key (stock_id, indice_id),
    foreign key (stock_id) references stocks(stock_id),
    foreign key (indice_id) references indices(indice_id)
);


