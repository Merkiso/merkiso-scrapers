-- stores definition

CREATE TABLE stores (
	id INTEGER NOT NULL, 
	name VARCHAR, 
	url VARCHAR, 
	domain VARCHAR, 
	logo VARCHAR, 
	created_at DATETIME, 
	updated_at DATETIME, 
	is_archived BOOLEAN NOT NULL, 
	PRIMARY KEY (id)
);


INSERT INTO stores
(id, name, url, "domain", logo, created_at, updated_at, is_archived)
VALUES(1, 'Euro', 'https://www.eurosupermercados.com.co', 'www.eurosupermercados.com.co', NULL, '2024-02-18 08:13:55.083180', '2024-02-18 08:13:55.083184', 0);

INSERT INTO stores
(id, name, url, "domain", logo, created_at, updated_at, is_archived)
VALUES(2, 'Olimpica', 'https://www.olimpica.com', 'www.olimpica.com', NULL, '2024-02-18 08:13:55.083185', '2024-02-18 08:13:55.083185', 0);

INSERT INTO stores
(id, name, url, "domain", logo, created_at, updated_at, is_archived)
VALUES(3, 'Exito', 'https://www.exito.com', 'www.exito.com', NULL, '2024-02-18 08:13:55.083186', '2024-02-18 08:13:55.083186', 0);

INSERT INTO stores
(id, name, url, "domain", logo, created_at, updated_at, is_archived)
VALUES(4, 'Jumbo', 'https://www.tiendasjumbo.co', 'www.tiendasjumbo.co', NULL, '2024-02-18 08:13:55.083187', '2024-02-18 08:13:55.083187', 0);

INSERT INTO stores
(id, name, url, "domain", logo, created_at, updated_at, is_archived)
VALUES(5, 'Carulla', 'https://www.carulla.com', 'www.carulla.com', NULL, '2024-02-18 08:13:55.083188', '2024-02-18 08:13:55.083188', 0);

INSERT INTO stores
(id, name, url, "domain", logo, created_at, updated_at, is_archived)
VALUES(6, 'Metro', 'https://www.tiendasmetro.co', 'www.tiendasmetro.co', NULL, '2024-02-18 08:13:55.083188', '2024-02-18 08:13:55.083189', 0);

