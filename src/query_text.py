
create_tipos_table = '''
CREATE TABLE Tipo_receta (
    recipe_type_id INT PRIMARY KEY,
    type_name VARCHAR(50) NOT NULL UNIQUE
);
'''

create_recetas_table = """
CREATE TABLE Recetas (
    recipe_id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    calories DECIMAL(10, 2),
    protein DECIMAL(10, 2),
    fat DECIMAL(10, 2),
    carbohydrates DECIMAL(10, 2),
    sugar DECIMAL(10, 2),
    fiber DECIMAL(10, 2),
    serving_weight DECIMAL(10, 2),
    recipe_type_id INT,
    recipe_url VARCHAR(255),
    health_score DECIMAL(5, 2),
    views INT,
    date DATE,
    FOREIGN KEY (recipe_type_id) REFERENCES Tipo_receta(recipe_type_id) ON DELETE SET NULL
);
"""

create_ingredientes_table = """
CREATE TABLE Ingredientes (
    ingredient_id SERIAL PRIMARY KEY,
    ingredient_name VARCHAR(100) NOT NULL UNIQUE,
    calories DECIMAL(10, 2),
    protein DECIMAL(10, 2),
    fat DECIMAL(10, 2),
    carbohydrates DECIMAL(10, 2),
    sugar DECIMAL(10, 2),
    fiber DECIMAL(10, 2)
);
"""

create_receta_ingredientes_table = """
CREATE TABLE Ingredientes_receta (
    recipe_ingredient_id SERIAL PRIMARY KEY,
    recipe_id INT NOT NULL,
    ingredient_id INT NOT NULL,
    weight DECIMAL(10, 2),
    calories DECIMAL(10, 2),
    protein DECIMAL(10, 2),
    fat DECIMAL(10, 2),
    carbohydrates DECIMAL(10, 2),
    sugar DECIMAL(10, 2),
    fiber DECIMAL(10, 2),
    serving_weight DECIMAL(10, 2),
    FOREIGN KEY (recipe_id) REFERENCES Recetas(recipe_id) ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id) REFERENCES Ingredientes(ingredient_id) ON DELETE CASCADE
);
"""
insert_tipos_query = """
INSERT INTO Tipo_receta (recipe_type_id, type_name)
VALUES (%s, %s);
"""

insert_receta_query = """
INSERT INTO Recetas (title, calories, protein, fat, carbohydrates, sugar, fiber, serving_weight, recipe_type_id, recipe_url, views, date, health_score)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""

insert_ingrediente_query = """
INSERT INTO Ingredientes (ingredient_name, calories, protein, fat, carbohydrates, sugar, fiber)
VALUES (%s, %s, %s, %s, %s, %s, %s);
"""

insert_receta_ingredientes_query = """
INSERT INTO Ingredientes_receta (recipe_id, ingredient_id, weight, calories, protein, fat, carbohydrates, sugar, fiber, serving_weight)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""