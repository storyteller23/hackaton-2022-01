DROP TABLE IF EXISTS subjects;
CREATE TABLE IF NOT EXISTS subjects(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	first_name TEXT NOT NULL,
	last_name TEXT NOT NULL,
	patronymic TEXT,
	iin TEXT NOT NULL,
	city TEXT NOT NULL,
	street TEXT NOT NULL,
	home_number TEXT NOT NULL,
	apartment_number TEXT,
	cadastral_number TEXT,
	area_size TEXT,
	notes TEXT,
	longitude REAL NOT NULL,
	latitude REAL NOT NULL,
	mark_color TEXT NOT NULL
);