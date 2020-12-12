SELECT * FROM user WHERE (age > 10) AND (class >= 5) AND (id  > 1);
SELECT * FROM user WHERE (class < 5) AND (age > 10) AND (id  > 1);
SELECT * FROM user WHERE (age <= 10) AND (class >= 5) AND (id  > 1);
SELECT * FROM user WHERE (class < 5) AND (age > 10) AND (id  > 1);
SELECT * FROM user WHERE (id > 1) AND (class < 5) OR (age <= 10);
SELECT * FROM user WHERE (id <= 1) AND (class < 5) OR (age <= 10);
