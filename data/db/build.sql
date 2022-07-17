CREATE TABLE IF NOT EXISTS accs(
    Account varchar,
    AccountType varchar
);

CREATE TABLE IF NOT EXISTS members(
    UserID integer DEFAULT 0 PRIMARY KEY,
    redeems integer DEFAULT 0,
    daily integer DEFAULT 0,
    rTime varchar DEFAULT 'None'
);

CREATE TABLE IF NOT EXISTS access_keys(
    access_key varchar DEFAULT 'None'
);
